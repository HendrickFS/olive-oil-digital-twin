import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from datetime import datetime

def generate_graphs(csv_path, output_dir):
    print(f"Loading data from {csv_path}...")
    # Read the dataset
    df = pd.read_csv(csv_path)
    
    # Filter for mixers and temperature
    df_mixers = df[df['thingId'].astype(str).str.contains('mixer', case=False, na=False)]
    if '_field' in df.columns:
        df_mixers = df_mixers[df_mixers['_field'] == 'temperature']
    
    if df_mixers.empty:
        print("No temperature data found for mixers.")
        return

    # Convert _time to datetime
    df_mixers['_time'] = pd.to_datetime(df_mixers['_time'])
    
    # Create a Year-Month column for grouping
    df_mixers['year_month'] = df_mixers['_time'].dt.to_period('M')
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Group by Year-Month and generate a plot for each
    for period, group in df_mixers.groupby('year_month'):
        plt.figure(figsize=(12, 6))
        
        # In case there are multiple mixers, we plot them separately
        for thingId, mixer_group in group.groupby('thingId'):
            # Sort by time just in case
            mixer_group = mixer_group.sort_values(by='_time')
            plt.plot(mixer_group['_time'], mixer_group['_value'], label=thingId)
            
        plt.title(f"Mixer Temperatures - {period.strftime('%B %Y')}")
        plt.xlabel("Time")
        plt.ylabel("Temperature")
        plt.legend()
        plt.grid(True)
        
        # Format x-axis dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.gcf().autofmt_xdate()
        
        # Save the plot
        output_filename = os.path.join(output_dir, f"mixer_temp_{period.strftime('%Y_%m')}.png")
        plt.savefig(output_filename, bbox_inches='tight')
        plt.close()
        print(f"Saved graph for {period} to {output_filename}")

if __name__ == "__main__":
    csv_file = "dataset-influx.csv"
    output_folder = "mixer_graphs"
    generate_graphs(csv_file, output_folder)
