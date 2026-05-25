#!/usr/bin/env python3
"""
generate_synthetic_batch.py

Generates artificial olive batch data representing physical extraction operations and oil quality.
Implements stochastic models heavily reliant on scientific literature describing physical olive oil extraction phenomena.

Can output batches as Dittoo formatted JSON mappings (via HTTP API) or as a bulk CSV dataset for machine learning.
"""

import argparse
import random
import json
import csv
import requests
import sys

def generate_noise(std=0.5):
    """Generate Gaussian noise around 0 to introduce realistic randomness to stochastic formulas."""
    return random.gauss(0, std)

def calculate_yield(oil_content, temp, time, defect, moisture):
    """
    Oil droplets coalescence modeled mathematically.
    Peaks near 27C and 45mins.
    """
    # fT(T) parabola centered at 27C
    fT = 1.0 - 0.005 * ((temp - 27.0)**2)
    fT = max(0.5, fT)
    
    # fTime(t) plateau at 45 mins
    fTime = 1.0
    if time > 45:
        fTime = 1.0 - 0.002 * ((time - 45)**2)
    elif time < 30:
        fTime = 1.0 - 0.005 * ((30 - time)**2)
    fTime = max(0.7, fTime)
    
    fDefect = max(0.6, 1.0 - (defect * 0.4))
    fMoisture = 1.0 if moisture < 50 else max(0.8, 1.0 - (moisture - 50)*0.01)
    
    base_yield = oil_content * fT * fTime * fDefect * fMoisture
    
    final_yield = base_yield + generate_noise(0.2)
    return round(max(0.0, min(oil_content, final_yield)), 2)

def calculate_phenols(mi, temp, time, water_ratio):
    """
    Simulates total phenols.
    Reduced by later maturation, higher times, and higher water ratio. Promoted up to 30C.
    """
    base_phenols = max(100, 600 - (mi * 50))
    
    gT = 1.0
    if temp < 30:
        gT = 1.0 + (temp - 20) * 0.02
    else:
        gT = 1.2 - (temp - 30) * 0.05
    
    gTime = 1.0
    if time > 30:
        gTime = max(0.5, 1.0 - (time - 30) * 0.015)
        
    gWater = max(0.4, 1.0 - (water_ratio * 0.02))
    
    phenols = base_phenols * gT * gTime * gWater + generate_noise(10.0)
    return round(max(0.0, phenols), 2)

def calculate_acidity(defect, time):
    acidity = 0.2 + (defect * 1.5) + ((time - 30)*0.005 if time > 30 else 0)
    acidity += generate_noise(0.02)
    return round(max(0.1, acidity), 2)
    
def calculate_peroxides(temp, time, phenols):
    peroxides = 5.0 + (temp - 25)*0.5 + (time - 30)*0.2
    # Phenols act as antioxidants, slightly reducing peroxides
    peroxides = peroxides - (phenols * 0.005)
    peroxides += generate_noise(0.5)
    return round(max(2.0, peroxides), 2)

def calculate_uv(acidity, peroxides):
    k232 = 1.5 + (peroxides - 5.0)*0.05 + generate_noise(0.05)
    k270 = 0.12 + (acidity - 0.2)*0.1 + generate_noise(0.01)
    deltaK = 0.005 + (acidity - 0.2)*0.005 + generate_noise(0.001)
    return round(max(1.0, k232), 2), round(max(0.05, k270), 2), round(max(-0.01, deltaK), 4)
    
def calculate_sensory(temp, phenols):
    fruity = 5.0
    if temp > 27:
        fruity -= (temp - 27) * 0.5
    else:
        fruity -= (27 - temp) * 0.1
    fruity = max(0.0, fruity) + generate_noise(0.2)
    
    # Bitter and pungent scale proportionally to phenols
    bitter = phenols * 0.01 + generate_noise(0.2)
    pungent = phenols * 0.012 + generate_noise(0.2)
    
    return round(max(0, fruity), 1), round(max(0, bitter), 1), round(max(0, pungent), 1)

def generate_batch(batch_seq):
    batch_id = f"batch{str(batch_seq).zfill(3)}"
    
    # Simulated Inputs (Uniform/Normal distributions within literature limits)
    mi = round(random.uniform(1.8, 4.5), 2)
    moisture = round(random.uniform(45.0, 58.0), 2)
    oil = round(random.uniform(14.0, 22.0), 2)
    defect = round(random.uniform(0.0, 1.0) * random.uniform(0.0, 1.0), 2) # mostly close to 0
    cultivar = random.choice(["Arbequina", "Picual", "Galega", "Cobrançosa"])
    
    temp = round(random.uniform(20.0, 32.0), 1)
    time = round(random.uniform(25.0, 55.0), 1)
    water_flow = round(random.uniform(0.0, 3.0), 2)
    water_ratio = round(random.uniform(0.0, 15.0), 1)
    
    # Calculation Pipeline (Forward Propagation)
    yield_perc = calculate_yield(oil, temp, time, defect, moisture)
    phenols = calculate_phenols(mi, temp, time, water_ratio)
    acidity = calculate_acidity(defect, time)
    peroxides = calculate_peroxides(temp, time, phenols)
    k232, k270, dK = calculate_uv(acidity, peroxides)
    fruity, bitter, pungent = calculate_sensory(temp, phenols)
    
    # IOC / EVOO conformity check
    is_evoo = bool(acidity <= 0.8 and peroxides <= 20.0 and k232 <= 2.50 and k270 <= 0.22 and dK <= 0.01 and defect <= 0.2 and fruity > 0.0)
    
    # Format for Eclipse Ditto (Artifact structure)
    thing = {
        "thingId": f"olive.batch:{batch_id}",
        "policyId": "olive.default:policy",
        "features": {
            "oliveParameters": {
                "properties": {
                    "maturationIndex": mi,
                    "moistureContent": moisture,
                    "oilContent": oil,
                    "defectIndex": defect,
                    "cultivar": cultivar
                }
            },
            "processParameters": {
                "properties": {
                    "malaxationTemperature": temp,
                    "malaxationTime": time,
                    "waterFlowRate": water_flow,
                    "waterToPasteRatio": water_ratio
                }
            },
            "oliveOilQuality": {
                "properties": {
                    "yieldPercentage": yield_perc,
                    "totalPhenols": phenols,
                    "freeAcidity": acidity,
                    "peroxideValue": peroxides,
                    "k232": k232,
                    "k270": k270,
                    "deltaK": dK,
                    "sensoryProfile": {
                        "fruity": fruity,
                        "bitter": bitter,
                        "pungent": pungent
                    },
                    "isEvooCompliant": is_evoo
                }
            }
        }
    }
    
    # Flattened format for CSV
    csv_row = {
        "batchId": batch_id,
        "cultivar": cultivar,
        "maturationIndex": mi,
        "moistureContent": moisture,
        "oilContent": oil,
        "defectIndex": defect,
        "malaxationTemperature": temp,
        "malaxationTime": time,
        "waterFlowRate": water_flow,
        "waterToPasteRatio": water_ratio,
        "yieldPercentage": yield_perc,
        "totalPhenols": phenols,
        "freeAcidity": acidity,
        "peroxideValue": peroxides,
        "k232": k232,
        "k270": k270,
        "deltaK": dK,
        "fruity": fruity,
        "bitter": bitter,
        "pungent": pungent,
        "isEvooCompliant": is_evoo
    }
    
    return thing, csv_row

def main():
    parser = argparse.ArgumentParser(description="Synthetic Olive Batch Generator")
    parser.add_argument("--count", type=int, default=1, help="Number of batches to generate")
    parser.add_argument("--csv", type=str, help="Output flat data to a CSV file (e.g., dataset.csv)")
    parser.add_argument("--publish", action="store_true", help="Publish generated batches to Ditto over HTTP API")
    parser.add_argument("--ditto-url", type=str, default="http://localhost:8080/api/2", help="Ditto HTTP API base URL")
    parser.add_argument("--user", type=str, default="ditto", help="Ditto username")
    parser.add_argument("--password", type=str, default="ditto", help="Ditto password")
    parser.add_argument("--dry-run", action="store_true", help="Generate and print first batch without saving")
    
    args = parser.parse_args()
    
    all_csv_rows = []
    
    for i in range(1, args.count + 1):
        thing_json, csv_row = generate_batch(i)
        all_csv_rows.append(csv_row)
        
        if args.dry_run and i == 1:
            print("--- DRY RUN: Simulated Batch Output ---")
            print(json.dumps(thing_json, indent=2))
        
        if args.publish:
            url = f"{args.ditto_url}/things/{thing_json['thingId']}"
            try:
                response = requests.put(url, json=thing_json, auth=(args.user, args.password))
                if response.status_code in [200, 201, 204]:
                    print(f"[{i}/{args.count}] Uploaded {thing_json['thingId']} to Ditto OK")
                else:
                    print(f"[{i}/{args.count}] Error uploading {thing_json['thingId']}: {response.status_code} {response.text}")
            except Exception as e:
                print(f"[{i}/{args.count}] HTTP Request failed: {e}")
                
    if args.csv:
        if len(all_csv_rows) > 0:
            keys = all_csv_rows[0].keys()
            try:
                with open(args.csv, 'w', newline='', encoding='utf-8') as f:
                    dict_writer = csv.DictWriter(f, fieldnames=keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(all_csv_rows)
                print(f"Successfully wrote {args.count} records to {args.csv}")
            except Exception as e:
                print(f"Failed to write CSV: {e}")
                
    if not args.publish and not args.csv and not args.dry_run:
        print("Generated data but no output action specified. Use --csv, --publish, or --dry-run.")

if __name__ == "__main__":
    main()
