import pandas as pd
import numpy as np
import psycopg2
from psycopg2 import sql
from datetime import datetime

# Database connection settings
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'volatility_forecasting',
    'user': 'postgres',
    'password': '114514'  # UPDATE THIS
}

def connect_db():
    """Create database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ Connected to PostgreSQL database")
        return conn
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        return None

def load_volatility_forecasts(conn):
    """Load GARCH forecasts (daily and 21d smoothed) and realised volatility"""
    print("\n1. Loading volatility forecasts...")
    
    # Load daily GARCH forecasts
    garch_df = pd.read_csv('outputs/forecasts/garch_volatility_forecast.csv')
    garch_df.columns = ['date', 'garch_forecast']
    garch_df['date'] = pd.to_datetime(garch_df['date'])
    
    print(f"   GARCH daily data shape: {garch_df.shape}")
    
    # Load 21d smoothed GARCH forecasts
    garch_21d_df = pd.read_csv('outputs/forecasts/garch_21d_smoothed_forecast.csv')
    garch_21d_df.columns = ['date', 'garch_21d_smoothed']
    garch_21d_df['date'] = pd.to_datetime(garch_21d_df['date'])
    
    print(f"   GARCH 21d smoothed shape: {garch_21d_df.shape}")
    
    # Load realised volatility
    vol_df = pd.read_csv('data/processed/realised_volatility_21d.csv')
    vol_df = vol_df[['Date', 'realised_vol_21d']]
    vol_df.columns = ['date', 'realised_volatility']
    vol_df['date'] = pd.to_datetime(vol_df['date'])
    
    print(f"   Realised vol data shape: {vol_df.shape}")
    
    # Merge all datasets
    merged_df = garch_df.merge(vol_df, on='date', how='inner')
    merged_df = merged_df.merge(garch_21d_df, on='date', how='left')  # Left join to keep all dates
    
    print(f"   Merged data shape: {merged_df.shape}")
    
    if len(merged_df) == 0:
        print("   ✗ Warning: No matching dates found!")
        return
    
    # Calculate errors for daily GARCH
    merged_df['forecast_error'] = merged_df['garch_forecast'] - merged_df['realised_volatility']
    merged_df['abs_error'] = merged_df['forecast_error'].abs()
    
    # Calculate errors for 21d smoothed GARCH (where available)
    merged_df['forecast_error_21d'] = merged_df['garch_21d_smoothed'] - merged_df['realised_volatility']
    merged_df['abs_error_21d'] = merged_df['forecast_error_21d'].abs()
    
    print(f"   Sample merged data:\n{merged_df.head()}")
    
    # Insert into database
    cursor = conn.cursor()
    inserted_count = 0
    
    for _, row in merged_df.iterrows():
        try:
            # Handle NaN values for 21d smoothed (first 20 days won't have values)
            garch_21d_val = None if pd.isna(row['garch_21d_smoothed']) else float(row['garch_21d_smoothed'])
            
            cursor.execute("""
                INSERT INTO volatility_forecasts 
                (date, garch_forecast, realised_volatility, forecast_error, abs_error, garch_21d_smoothed)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (date) DO UPDATE SET
                    garch_forecast = EXCLUDED.garch_forecast,
                    realised_volatility = EXCLUDED.realised_volatility,
                    forecast_error = EXCLUDED.forecast_error,
                    abs_error = EXCLUDED.abs_error,
                    garch_21d_smoothed = EXCLUDED.garch_21d_smoothed;
            """, (
                row['date'].date(),
                float(row['garch_forecast']),
                float(row['realised_volatility']),
                float(row['forecast_error']),
                float(row['abs_error']),
                garch_21d_val
            ))
            inserted_count += 1
        except Exception as e:
            print(f"   ✗ Error inserting row {row['date']}: {e}")
            break
    
    conn.commit()
    print(f"✓ Loaded {inserted_count} rows into volatility_forecasts")
    cursor.close()

def load_model_performance(conn):
    """Load model comparison metrics"""
    print("\n2. Loading model performance...")
    
    # Updated metrics from your new table
    model_data = [
        ('Naive Persistence', '2022-2024', 0.000351, 0.000592, 753),
        ('ETS', '2022-2024', 0.000351, 0.000592, 753),
        ('GARCH Daily', '2022-2024', 0.001444, 0.001963, 753),
        ('GARCH 21d Smoothed', '2022-2024', 0.000974, 0.001222, 753)
    ]
    
    cursor = conn.cursor()
    
    for model in model_data:
        cursor.execute("""
            INSERT INTO model_performance 
            (model_name, evaluation_period, mae, rmse, observation_count)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (model_name) DO UPDATE SET
                evaluation_period = EXCLUDED.evaluation_period,
                mae = EXCLUDED.mae,
                rmse = EXCLUDED.rmse,
                observation_count = EXCLUDED.observation_count;
        """, model)
    
    conn.commit()
    print(f"✓ Loaded {len(model_data)} rows into model_performance")
    cursor.close()

def load_volatility_regimes(conn):
    """Calculate and load volatility regimes"""
    print("\n3. Loading volatility regimes...")
    
    # Load realised volatility
    vol_df = pd.read_csv('data/processed/realised_volatility_21d.csv')
    vol_df = vol_df[['Date', 'realised_vol_21d']]
    vol_df.columns = ['date', 'realised_volatility']
    vol_df['date'] = pd.to_datetime(vol_df['date'])
    
    # Calculate percentile ranks
    vol_df['percentile_rank'] = vol_df['realised_volatility'].rank(pct=True) * 100
    
    # Classify regimes
    def classify_regime(percentile):
        if percentile < 33:
            return 'Low'
        elif percentile < 67:
            return 'Medium'
        else:
            return 'High'
    
    vol_df['regime'] = vol_df['percentile_rank'].apply(classify_regime)
    
    # Insert into database
    cursor = conn.cursor()
    inserted_count = 0
    
    for _, row in vol_df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO volatility_regimes 
                (date, realised_volatility, regime, percentile_rank)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (date) DO UPDATE SET
                    realised_volatility = EXCLUDED.realised_volatility,
                    regime = EXCLUDED.regime,
                    percentile_rank = EXCLUDED.percentile_rank;
            """, (
                row['date'].date(),
                float(row['realised_volatility']),
                row['regime'],
                float(row['percentile_rank'])
            ))
            inserted_count += 1
        except Exception as e:
            print(f"   ✗ Error inserting row {row['date']}: {e}")
            break  # Stop on first error
    
    conn.commit()
    print(f"✓ Loaded {inserted_count} rows into volatility_regimes")
    cursor.close()

def verify_data(conn):
    """Verify data was loaded correctly"""
    print("\n4. Verifying data...")
    
    cursor = conn.cursor()
    
    # Check row counts
    tables = ['volatility_forecasts', 'model_performance', 'volatility_regimes']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"   ✓ {table}: {count} rows")
    
    # Show sample data from volatility_forecasts
    print("\n   Sample from volatility_forecasts (most recent 3):")
    cursor.execute("""
        SELECT date, 
               ROUND(garch_forecast::numeric, 6) as garch, 
               ROUND(realised_volatility::numeric, 6) as realised,
               ROUND(abs_error::numeric, 6) as error
        FROM volatility_forecasts 
        ORDER BY date DESC 
        LIMIT 3;
    """)
    for row in cursor.fetchall():
        print(f"   {row}")
    
    # Show model performance
    print("\n   Model performance:")
    cursor.execute("""
        SELECT model_name, 
               ROUND(mae::numeric, 6) as mae,
               ROUND(rmse::numeric, 6) as rmse
        FROM model_performance 
        ORDER BY mae;
    """)
    for row in cursor.fetchall():
        print(f"   {row}")
    
    cursor.close()

def main():
    """Main execution function"""
    print("=" * 60)
    print("Loading ETF Volatility Forecasting Data to PostgreSQL")
    print("=" * 60)
    
    # Connect to database
    conn = connect_db()
    if not conn:
        return
    
    try:
        # Load all tables
        load_volatility_forecasts(conn)
        load_model_performance(conn)
        load_volatility_regimes(conn)
        
        # Verify
        verify_data(conn)
        
        print("\n" + "=" * 60)
        print("✓ All data loaded successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Open pgAdmin4 and verify the tables")
        print("2. Run the SQL queries (coming next)")
        print("3. Connect Power BI to this database")
        
    except Exception as e:
        print(f"\n✗ Error during data loading: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    
    finally:
        conn.close()
        print("\n✓ Database connection closed")

if __name__ == "__main__":
    main()