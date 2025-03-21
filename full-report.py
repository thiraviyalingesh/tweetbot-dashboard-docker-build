# Import necessary libraries
import streamlit as st
import pymongo
import os
from dotenv import load_dotenv
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
from logger import setup_logger, log_dataframe
import io

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debugger.log"),
        logging.StreamHandler()
    ]
)
logger = setup_logger(__name__)

# Page configuration with dark theme
st.set_page_config(
    page_title="Tweet Engagements Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Dark theme styling with smaller KPI cards and cream browser background
st.markdown("""
<style>
    .main, .main .block-container, body, [data-testid="stAppViewContainer"] {
        background-color:#f0f4f8 !important;
    }
    
    /* Fix for stApp wrapper */
    .stApp {
        background-color: #f5f3e8 !important;
    }
    
    /* Dark themed containers on cream background */
    .metric-container {
        text-align: center; 
        background-color: #1e1e1e; 
        padding: 12px; 
        border-radius: 8px; 
        margin: 6px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        border-left: 3px solid #3498db;
        height: auto;
        color: #f0f0f0;
    }
    
    /* Success metrics container */
    .success-metric-container {
        text-align: center; 
        background-color: #1e1e1e; 
        padding: 12px; 
        border-radius: 8px; 
        margin: 6px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        border-left: 3px solid #27ae60;
        height: auto;
        color: #f0f0f0;
    }
    
    /* Metric title */
    .metric-title {
        color: #3498db;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 6px;
    }
    
    /* Success metric title */
    .success-metric-title {
        color: #27ae60;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 6px;
    }
    
    /* Small big number display */
    .big-number {
        color: #3498db; 
        font-size: 32px;
        font-weight: 700;
        margin: 4px 0;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }
    
    /* Success big number display */
    .success-big-number {
        color: #27ae60; 
        font-size: 32px;
        font-weight: 700;
        margin: 4px 0;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }
    
    /* Chart container */
    .chart-container {
        padding: 15px;
        border-radius: 8px;
        background-color: #1e1e1e;
        margin: 12px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        color: #f0f0f0;
    }
    
    /* Chart borders */
    .engagement-chart {
        border-left: 3px solid #1DA1F2;
    }
    
    .success-chart {
        border-left: 3px solid #27ae60;
    }
    
    /* Chart title */
    .chart-title {
        color: #e0e0e0;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 12px;
    }
    
    /* Section headers */
    h1, h2, h3, h4 {
        font-weight: 600;
        color: #333333; /* Dark text on cream background */
        margin: 0px 0 0px 0;  /* Reduced top margin from 15px to 5px */
        padding-top: 0px;      /* Added small top padding */
    }
    
    /* Button styling */
    .stButton > button, .stDownloadButton > button {
        width: 100% !important;
        height: 60px !important;
        border-radius: 5px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Refresh button styling (Twitter blue) */
    .stButton > button {
        background-color: #1DA1F2 !important;
    }
    
    /* Excel button styling (Excel green) */
    .stDownloadButton > button {
        background-color: #008000 !important;
    }
    
    /* Hover effects */
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    }
    
    .refresh-button {
    background: linear-gradient(45deg, #2193b0, #6dd5ed);
    color: white;
    border: none;
    border-radius: 30px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    display: inline-block;
    text-align: center;
    text-decoration: none;
    position: relative;
    overflow: hidden;
    z-index: 10;
    }

    .refresh-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 7px 20px rgba(0,0,0,0.3);
    }

    .refresh-button::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, #6dd5ed, #2193b0);
        opacity: 0;
        z-index: -1;
        transition: opacity 0.3s ease;
    }

    .refresh-button:hover::after {
        opacity: 1;
    }

    /* Animated text styles */
    .text7 {
    color: white;
    font-weight: bold;
    font-size: 26px;
    box-sizing: content-box;
    -webkit-box-sizing: content-box;
    height: 40px;
    display: flex;
    margin-top: 10px;
    justify-content: center;
    }
    .text7 .words {
    overflow: hidden;
    position: relative;
    top: 50%;
    }
    .text7 span {
    display: block;
    padding-left: 6px;
    padding-top: 5px;
    color: #956afa;
    animation: text7-animation 4s infinite;
    }
    @keyframes text7-animation {
    10% {
        -webkit-transform: translateY(-102%);
        transform: translateY(-102%);
    }
    25% {
        -webkit-transform: translateY(-100%);
        transform: translateY(-100%);
    }
    35% {
        -webkit-transform: translateY(-202%);
        transform: translateY(-202%);
    }
    50% {
        -webkit-transform: translateY(-200%);
        transform: translateY(-200%);
    }
    60% {
        -webkit-transform: translateY(-302%);
        transform: translateY(-302%);
    }
    75% {
        -webkit-transform: translateY(-300%);
        transform: translateY(-300%);
    }
    85% {
        -webkit-transform: translateY(-402%);
        transform: translateY(-402%);
    }
    100% {
        -webkit-transform: translateY(-400%);
        transform: translateY(-400%);
    }
    }
    
    .text7 {
  color: black;
  font-weight: bold;
  font-size: 26px;
  box-sizing: content-box;
  -webkit-box-sizing: content-box;
  height: 40px;
  display: flex;
}
.text7 .words {
  overflow: hidden;
  position: relative;
  top: 50%;
}
.text7 span {
  display: block;
  padding-left: 6px;
  padding-top: 5px;
  color: #956afa;
  animation: text7-animation 4s infinite;
}
@keyframes text7-animation {
  10% {
    -webkit-transform: translateY(-102%);
    transform: translateY(-102%);
  }
  25% {
    -webkit-transform: translateY(-100%);
    transform: translateY(-100%);
  }
  35% {
    -webkit-transform: translateY(-202%);
    transform: translateY(-202%);
  }
  50% {
    -webkit-transform: translateY(-200%);
    transform: translateY(-200%);
  }
  60% {
    -webkit-transform: translateY(-302%);
    transform: translateY(-302%);
  }
  75% {
    -webkit-transform: translateY(-300%);
    transform: translateY(-300%);
  }
  85% {
    -webkit-transform: translateY(-402%);
    transform: translateY(-402%);
  }
  100% {
    -webkit-transform: translateY(-400%);
    transform: translateY(-400%);
  }
}

/* Elegant rich cards with smooth hover */
.elegant-card {
    background: linear-gradient(to right, #B8860B, #FFD700);
    border-radius: 15px;
    padding: 25px;
    color: white;
    transition: all 0.4s ease;
    box-shadow: 0 10px 20px rgba(108, 60, 0, 0.2);
    border: none;
    position: relative;
    overflow: hidden;
    height: 100%;
}

.elegant-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(230, 178, 93, 0.3), rgba(108, 60, 0, 0.1));
    opacity: 0;
    transition: opacity 0.4s ease;
    z-index: 1;
    border-radius: 15px;
}

.elegant-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 15px 30px rgba(108, 60, 0, 0.3);
}

.elegant-card:hover::before {
    opacity: 1;
}

.elegant-card .card-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 12px;
    position: relative;
    z-index: 2;
    letter-spacing: 0.5px;
}

.elegant-card .card-value {
    font-size: 48px;
    font-weight: 700;
    margin: 15px 0;
    position: relative;
    z-index: 2;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.elegant-card.primary {
    background: linear-gradient(135deg, #6c3c00, #e6b25d);
}

.elegant-card.secondary {
    background: linear-gradient(135deg, #004e6c, #5dbfe6);
}
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Get MongoDB connection details from environment variables
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

# Twitter color palette
TWITTER_COLORS = {
    'blue': '#1DA1F2',
    'black': '#14171A',
    'dark_gray': '#657786',
    'light_gray': '#AAB8C2',
    'extra_light_gray': '#E1E8ED',
    'extra_extra_light_gray': '#F5F8FA',
    'white': '#FFFFFF'
}

def get_total_engagements():
    """
    Function to fetch the total number of tweet engagements.
    Each unique _id represents a distinct engagement.
    
    Returns:
        int: Total count of unique engagements
    """
    try:
        logger.debug("Fetching total engagements")
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        
        # Use the twitter_actions collection
        collection = db["twitter_actions"]
        
        # Count total unique engagements based on _id
        # Each document has a unique _id so this counts all documents
        total_count = collection.estimated_document_count()
        
        # Close connection
        client.close()
        
        logger.debug(f"Found {total_count} total engagements")
        return total_count
    except Exception as e:
        logger.error(f"MongoDB Connection Error: {str(e)}")
        st.error(f"MongoDB Connection Error: {str(e)}")
        return 0

def get_successful_engagements():
    """
    Function to fetch the total number of successful tweet engagements.
    Looks for a 'Success' or similar field in the documents and counts
    those that have a truthy value.
    
    Returns:
        int: Total count of successful engagements
    """
    try:
        logger.debug("Fetching successful engagements")
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        
        # Use the twitter_actions collection
        collection = db["twitter_actions"]
        
        # Count documents that are either:
        # 1. Have "Success" in result field
        # 2. Have "Failed" in result but "Success" in rerun
        successful_count = collection.count_documents({
            "$or": [
                {"result": {"$regex": "Success", "$options": "i"}},  # Case insensitive Success in result
                {
                    "$and": [
                        {"result": {"$regex": "Failed", "$options": "i"}},  # Failed attempts
                        {"rerun": {"$regex": "Success", "$options": "i"}}   # But succeeded in rerun
                    ]
                }
            ]
        })
        
        client.close()
        return successful_count
        
    except Exception as e:
        logger.error(f"MongoDB Connection Error: {str(e)}")
        st.error(f"MongoDB Connection Error: {str(e)}")
        return 0

def get_success_ratio():
    """
    Calculate the success ratio percentage.
    
    Returns:
        float: Percentage of successful engagements
    """
    try:
        logger.debug("Calculating success ratio")
        # Get total and successful counts
        total = get_total_engagements()
        successful = get_successful_engagements()
        
        # Calculate percentage
        if total > 0:
            ratio = (successful / total) * 100
            logger.debug(f"Success ratio: {ratio:.2f}%")
            return ratio
        else:
            logger.warning("No engagements found for success ratio calculation")
            return 0
    except Exception as e:
        logger.error(f"Error calculating success ratio: {str(e)}")
        return 0

def get_engagement_time_series():
    """
    Fetches engagement time series data for exactly the last 7 days.
    """
    try:
        logger.debug("Fetching engagement time series data")
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        collection = db["twitter_actions"]
        
        # Get current date in UTC and set time to end of day
        end_date = datetime.utcnow().replace(hour=23, minute=59, second=59)
        # Get start date as 6 days ago (to get exactly 7 days including today)
        start_date = (end_date - timedelta(days=6)).replace(hour=0, minute=0, second=0)
        
        pipeline = [
            {
                "$match": {
                    "date": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$date"
                        }
                    },
                    "engagements": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        result = list(collection.aggregate(pipeline))
        client.close()
        
        # Convert to DataFrame and handle missing dates
        df = pd.DataFrame(result)
        if not df.empty:
            df = df.rename(columns={"_id": "date", "engagements": "engagements"})
            df['date'] = pd.to_datetime(df['date'])
            
            # Create complete date range for exactly 7 days
            date_range = pd.date_range(start=start_date.date(), end=end_date.date(), freq='D')
            all_dates = pd.DataFrame({'date': date_range})
            
            # Merge with actual data and fill missing values
            df = pd.merge(all_dates, df, on='date', how='left')
            df['engagements'] = df['engagements'].fillna(0)
            
            return df
        return pd.DataFrame()
        
    except Exception as e:
        logger.error(f"Error fetching time series data: {str(e)}")
        return pd.DataFrame()

def get_celebrity_engagement_data():
    """
    Fetches and aggregates engagement counts by celebrity tweet with case-insensitive matching.
    """
    try:
        print("Starting celebrity data fetch with case-insensitive matching...")
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        collection = db["twitter_actions"]
        
        # Case-insensitive aggregation pipeline
        pipeline = [
            {
                "$match": {
                    "username": {
                        "$exists": True, 
                        "$ne": None
                    }
                }
            },
            {
                # Convert username to lowercase for grouping
                "$group": {
                    "_id": {"$toLower": "$username"},  # Case-insensitive grouping
                    "originalName": {"$first": "$username"},  # Keep one original username
                    "engagements": {"$sum": 1}
                }
            },
            {
                "$sort": {"engagements": -1}
            },
            {
                "$limit": 5
            }
        ]
        
        result = list(collection.aggregate(pipeline))
        print(f"Aggregation result: {result}")
        
        client.close()
        
        if result:
            # Convert to DataFrame with proper column names
            df = pd.DataFrame([
                {
                    "username": doc["originalName"],
                    "engagements": doc["engagements"]
                } for doc in result
            ])
            
            # Clean up usernames (remove @ if present)
            df['username'] = df['username'].apply(
                lambda x: x.replace('@', '') if isinstance(x, str) and x.startswith('@') else x
            )
            
            print("Final DataFrame with case-insensitive aggregation:")
            print(df)
            return df
        
        print("No celebrity engagement data found")
        return pd.DataFrame(columns=['username', 'engagements'])
        
    except Exception as e:
        print(f"Error in celebrity data fetch: {str(e)}")
        return pd.DataFrame(columns=['username', 'engagements'])

def get_user_engagement_data():
    """
    Fetches and aggregates engagement counts by Twitter users.
    Returns top 5 users with highest engagement counts.
    
    Returns:
        pandas.DataFrame: DataFrame containing user names and their engagement counts
        Columns: ['name', 'engagements']
    
    Raises:
        Returns empty DataFrame with appropriate error message on failure
    """
    try:
        logger.debug("Fetching user engagement data")
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        collection = db["twitter_actions"]
        
        pipeline = [
            {"$group": {
                "_id": "$name",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        
        result = list(collection.aggregate(pipeline))
        client.close()
        
        df = pd.DataFrame(result)
        if not df.empty:
            df = df.rename(columns={"_id": "name", "count": "engagements"})
            logger.debug(f"Found {len(df)} user records")
            return df
        
        logger.warning("No user engagement data found")
        st.error("No user engagement data available")
        return pd.DataFrame(columns=['name', 'engagements'])
        
    except Exception as e:
        logger.error(f"Error fetching user data: {str(e)}")
        st.error("Failed to fetch user engagement data")
        return pd.DataFrame(columns=['name', 'engagements'])
        
def get_rerun_comparison_data():
    """
    Replicates Excel formula logic for comparing Initial Run vs Rerun metrics.
    Excel formulas reference Analysis Overall sheet cells:
    D7, D12 (Likes)
    D8, D13 (Reposts/Retweets)
    D9, D14 (Comments)
    """
    try:
        logger.debug("Fetching rerun comparison data using Excel formula logic")
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        collection = db["twitter_actions"]

        # Pipeline for initial run (equivalent to D7, D8, D9)
        initial_pipeline = [
            {
                "$match": {
                    "result": {"$regex": "success", "$options": "i"}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$cond": [
                            {"$regexMatch": {"input": "$action", "regex": "like", "options": "i"}},
                            "likes",
                            {
                                "$cond": [
                                    {"$regexMatch": {"input": "$action", "regex": "repost|retweet", "options": "i"}},
                                    "retweets",  # Changed from "reposts" to "retweets"
                                    "comments"
                                ]
                            }
                        ]
                    },
                    "count": {"$sum": 1}
                }
            }
        ]

        # Pipeline for rerun (equivalent to D12, D13, D14)
        rerun_pipeline = [
            {
                "$match": {
                    "$or": [
                        {"result": {"$regex": "success", "$options": "i"}},
                        {"rerun": {"$regex": "success", "$options": "i"}}
                    ]
                }
            },
            {
                "$group": {
                    "_id": {
                        "$cond": [
                            {"$regexMatch": {"input": "$action", "regex": "like", "options": "i"}},
                            "likes",
                            {
                                "$cond": [
                                    {"$regexMatch": {"input": "$action", "regex": "repost|retweet", "options": "i"}},
                                    "retweets",  # Changed from "reposts" to "retweets"
                                    "comments"
                                ]
                            }
                        ]
                    },
                    "count": {"$sum": 1}
                }
            }
        ]

        initial_results = {doc["_id"]: doc["count"] for doc in collection.aggregate(initial_pipeline)}
        rerun_results = {doc["_id"]: doc["count"] for doc in collection.aggregate(rerun_pipeline)}

        client.close()

        # Structure data like Excel series
        metrics = {
            "initial": {
                "likes": initial_results.get("likes", 0),
                "retweets": initial_results.get("retweets", 0),  # Changed from "reposts" to "retweets"
                "comments": initial_results.get("comments", 0)
            },
            "rerun": {
                "likes": rerun_results.get("likes", 0),
                "retweets": rerun_results.get("retweets", 0),  # Changed from "reposts" to "retweets"
                "comments": rerun_results.get("comments", 0)
            }
        }

        # If no data found, don't use hardcoded values
        if all(v == 0 for v in metrics["initial"].values()) and all(v == 0 for v in metrics["rerun"].values()):
            logger.warning("No rerun comparison data found")
            return metrics

        logger.debug(f"Metrics found - Initial: {metrics['initial']}, Rerun: {metrics['rerun']}")
        return metrics

    except Exception as e:
        logger.error(f"Error fetching rerun comparison data: {str(e)}")
        return {
            "initial": {"likes": 0, "retweets": 0, "comments": 0},  # Changed from "reposts" to "retweets"
            "rerun": {"likes": 0, "retweets": 0, "comments": 0}  # Changed from "reposts" to "retweets"
        }
def get_engagement_time_series_with_filter(start_date=None, end_date=None):
    """
    Fetches engagement time series data for a specified date range.
    
    Args:
        start_date (datetime, optional): Start date for filtering
        end_date (datetime, optional): End date for filtering
    
    Returns:
        pandas.DataFrame: DataFrame with date and engagement counts
    """
    try:
        logger.debug(f"Fetching engagement time series data from {start_date} to {end_date}")
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        collection = db["twitter_actions"]
        
        # If no dates provided, default to last 7 days
        if start_date is None or end_date is None:
            # Get current date in UTC and set time to end of day
            end_date = datetime.utcnow().replace(hour=23, minute=59, second=59)
            # Get start date as 6 days ago (to get exactly 7 days including today)
            start_date = (end_date - timedelta(days=6)).replace(hour=0, minute=0, second=0)
        
        pipeline = [
            {
                "$match": {
                    "date": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$date"
                        }
                    },
                    "engagements": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        result = list(collection.aggregate(pipeline))
        client.close()
        
        # Convert to DataFrame and handle missing dates
        df = pd.DataFrame(result)
        if not df.empty:
            df = df.rename(columns={"_id": "date", "engagements": "engagements"})
            df['date'] = pd.to_datetime(df['date'])
            
            # Create complete date range for the filtered period
            date_range = pd.date_range(start=start_date.date(), end=end_date.date(), freq='D')
            all_dates = pd.DataFrame({'date': date_range})
            
            # Merge with actual data and fill missing values
            df = pd.merge(all_dates, df, on='date', how='left')
            df['engagements'] = df['engagements'].fillna(0)
            
            return df
        return pd.DataFrame()
        
    except Exception as e:
        logger.error(f"Error fetching time series data: {str(e)}")
        return pd.DataFrame()
def generate_raw_data_excel():
    """
    Generate an Excel file with all raw data directly from the database.
    Handles potential data type issues with robust error handling.
    
    Returns:
        bytes: Excel file as bytes
    """
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        collection = db["twitter_actions"]
        
        # Fetch ALL data from the database without any filtering
        all_data = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB IDs
        
        # Convert to DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            
            # Handle date conversion with robust error handling
            if 'date' in df.columns:
                df['date'] = df['date'].apply(lambda x: str(x) if not isinstance(x, (str, datetime)) else x)
                
                def safe_date_parse(date_str):
                    try:
                        if pd.isna(date_str) or date_str == '':
                            return date_str
                        return pd.to_datetime(date_str)
                    except:
                        return date_str
                
                df['date'] = df['date'].apply(safe_date_parse)
                df['date'] = df['date'].apply(
                    lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, datetime) else x
                )
            
            # Convert to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            excel_data = output.getvalue()
            
            logger.debug(f"Excel generation successful. Data size: {len(excel_data)} bytes")
            return excel_data
        else:
            logger.warning("No data found for Excel generation")
            return None
        
    except Exception as e:
        logger.error(f"Error generating Excel file: {str(e)}")
        return None
    finally:
        if 'client' in locals():
            client.close()
    
def main():
    """Main function to run the Streamlit dashboard."""
    logger.debug("Starting dashboard application")
    
    # Dashboard Title
    st.markdown("""
        <h1 style='color: #333333; text-align: center; padding: 0px 0 10px 0; margin: 0;'>
            BUZZTRACKER'S TWEETBOT DASHBOARD
        </h1>
    """, unsafe_allow_html=True)
    
    # # Single column for refresh button
    # col1, col2 = st.columns([1, 11])
    
    # Refresh Button
    # with col1:
    #     if st.button("🔄 Refresh", use_container_width=True):
    #         logger.debug("Manual refresh triggered")
    #         st.rerun()
    
    # # Add a horizontal line after the controls
    # st.markdown("<hr style='margin: 1em 0; padding: 0;'>", unsafe_allow_html=True)
    
    # Single column for refresh button and download button
    col1, col2, col3 = st.columns([1, 10, 1])  # Changed from [1, 11] to [1, 1, 10]

    # Refresh Button
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            logger.debug("Manual refresh triggered")
            st.rerun()
            
    with col3:
        # Direct download of raw data as Excel when button is clicked
        if st.download_button(
            label="Download Excel",
            data=generate_raw_data_excel(),  # Generate Excel data directly on click
            file_name=f"Buzztracker_Tweetbot_DB_Data_{datetime.now().strftime('%Y-%m-%d')}.xlsx", 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        ):
            logger.debug("Raw data export triggered")
    
    # Get all required data
    total_engagements = get_total_engagements()
    successful_engagements = get_successful_engagements()
    success_ratio = get_success_ratio()
    celebrity_data = get_celebrity_engagement_data()
    user_data = get_user_engagement_data()
    time_series_data = get_engagement_time_series()
    rerun_data = get_rerun_comparison_data()

    # Create a 2-column layout: Left for KPIs (1/3) and Right for pie chart (2/3)
    left_col, right_col = st.columns([1, 2])

    # Left column - Stacked KPI cards
    with left_col:
        # Total Engagements Card
        st.markdown(
            f"""
            <div class="elegant-card primary" style="padding: 0.9rem; height: 175px; margin-bottom: 10px;">
                <div class="card-title" style=" text-align: center; font-size: 1.7rem;">Total Engagements</div>
                <div class="card-value" style="text-align: center; font-size: 3.2rem;">{total_engagements}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

        # Successful Engagements Card
        st.markdown(
            f"""
            <div class="elegant-card secondary" style="padding: 0.6rem; height: 175px;margin-bottom: 10px;">
                <div class="card-title" style=" text-align: center; font-size: 1.7rem;">Successful Engagements</div>
                <div class="card-value" style="text-align: center; font-size: 3.2rem;">{successful_engagements}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

    # Right column - Large pie chart
    with right_col:
        st.markdown("""
            <div style="background: #722F37; padding: 10px; border-radius: 10px; margin: 10px 0;">
                <h2 style="text-align: center; color: #F5DEB3; font-size: 24px; margin: 0;">Success Ratio</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Success ratio donut chart
        fig_success = go.Figure(data=[go.Pie(
            labels=['Successful', 'Failed'],
            values=[success_ratio, 100 - success_ratio],
            hole=0.7,
            textinfo='none',
            marker=dict(
                colors=['#3B7D23', '#D9D9D9'],
                line=dict(color='white', width=2)
            )
        )])
        
        fig_success.update_layout(
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=250,
            width=None,
            annotations=[dict(
                text=f"{success_ratio:.1f}%",
                x=0.5, y=0.5,
                font=dict(size=28, color='#6c3c00', family='Arial Black'),
                showarrow=False
            )]
        )
        
        st.plotly_chart(fig_success, use_container_width=True)

    # Rerun Facility and Tweets Engagements headings
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div style="background: #722F37; padding: 15px; border-radius: 15px; margin: 20px 0;">
                <h2 style="color: #F5DEB3; font-size: 24px; margin: 0;">Rerun Facility to increase our Success rate</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="background: #722F37; padding: 15px; border-radius: 15px; margin: 20px 0;">
                <h2 style="color: #F5DEB3; font-size: 24px; margin: 0;">Tweets Engagements over date</h2>
            </div>
        """, unsafe_allow_html=True)

    # Left column - Performance comparison chart
    with col1:
        # Create figure
        fig_combined = go.Figure()
        
        # Add Initial Run bars (positioned at x=0,1,2)
        fig_combined.add_trace(go.Bar(
            name='Initial Run',
            x=[0, 1, 2],  # Left side positions
            y=[
                rerun_data['initial']['likes'],
                rerun_data['initial']['retweets'],
                rerun_data['initial']['comments']
            ],
            marker_color=['#5CB338', '#FB4141', '#FFC145'],  # Keeping the original bar colors
            text=[
                rerun_data['initial']['likes'],
                rerun_data['initial']['retweets'],
                rerun_data['initial']['comments']
            ],
            textposition='outside',
            textfont=dict(size=14   , color='#000000', family='Arial Black'),
            width=0.8,
            showlegend=False  # Remove legend
        ))
        
        # Add Rerun bars (positioned at x=4,5,6)
        fig_combined.add_trace(go.Bar(
            name='Rerun',
            x=[4, 5, 6],  # Right side positions
            y=[
                rerun_data['rerun']['likes'],
                rerun_data['rerun']['retweets'],
                rerun_data['rerun']['comments']
            ],
            marker_color=['#5CB338', '#FB4141', '#FFC145'],  # Keeping the original bar colors
            text=[
                rerun_data['rerun']['likes'],
                rerun_data['rerun']['retweets'],
                rerun_data['rerun']['comments']
            ],
            textposition='outside',
            textfont=dict(size=14, color='#000000', family='Arial Black'),
            width=0.8,
            showlegend=False  # Remove legend
        ))
        
        # Update layout with improved background
        fig_combined.update_layout(
            # Background colors
            plot_bgcolor='#FAF3E0',  # Cream background color
            paper_bgcolor='#FAF3E0', # Same cream background
            
            # Size and margins
            height=520,  # Increased height for better visualization
            margin=dict(l=40, r=40, t=60, b=50),  # Adjusted margins
            
            # Hide axes
            xaxis=dict(
                showgrid=False,
                showticklabels=False,  # Hide tick labels for a clean look
                showline=False,
                zeroline=False  # Remove zero line
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,  # Hide tick labels
                showline=False,
                zeroline=False  # Remove zero line
            ),
            
            # Add title with better styling
            title=dict(
                text='Initial Run vs Rerun Performance',
                font=dict(size=16, color='#333333', family='Arial, sans-serif'),
                x=0.5,  # Center title
                y=0.98  # Adjusted position
            )
        )

        # Find the maximum value across all bars
        max_value = max([
            rerun_data['initial']['likes'],
            rerun_data['initial']['retweets'],
            rerun_data['initial']['comments'],
            rerun_data['rerun']['likes'],
            rerun_data['rerun']['retweets'],
            rerun_data['rerun']['comments']
        ])

        # Add some padding (20% more than max value)
        y_axis_max = max_value * 1.2

        # Update the layout with the new y-axis range
        fig_combined.update_layout(
            yaxis=dict(
                range=[0, y_axis_max],  # Set the range from 0 to max_value + 20%
                showgrid=False,
                showticklabels=False,
                showline=False,
                zeroline=False
            )
        )

        # Add a border around the entire plot
        fig_combined.update_layout(
            shapes=[
                dict(
                    type='rect',
                    xref='paper', yref='paper',
                    x0=0, y0=0, x1=1, y1=1,
                    line=dict(color='#b0bec5', width=1),  # Softer gray border
                    fillcolor='rgba(0,0,0,0)'
                )
            ]
        )

        # Add labels above each set with adjusted positioning
        fig_combined.add_annotation(
            x=0.15,  # Moved left (was 0.25)
            y=1.1,
            text="Initial Run",
            showarrow=False,
            font=dict(size=14, color='#000000', family='Arial Black'),
            xref="paper",
            yref="paper",
            xanchor='center',  # Center align text
            yanchor='middle'
        )
        fig_combined.add_annotation(
            x=0.85,  # Moved right (was 0.75)
            y=1.1,
            text="Rerun",
            showarrow=False,
            font=dict(size=14, color='#000000', family='Arial Black'),
            xref="paper",
            yref="paper",
            xanchor='center',  # Center align text
            yanchor='middle'
        )

        # Center the main title
        fig_combined.update_layout(
            title=dict(
                text='Initial Run vs Rerun Performance',
                font=dict(size=16, color='#333333', family='Arial Black'),
                x=0.5,
                y=0.95,
                xanchor='center',
                yanchor='top'
            )
        )

        # Add metric labels below bars with centered positioning
        for i, metric in enumerate(['Likes', 'Retweets', 'Comments']):
            # Labels for Initial Run
            fig_combined.add_annotation(
                x=i,
                y=-0.1,
                text=metric,
                showarrow=False,
                font=dict(size=12, color='#000000', family='Arial Black'),
                yshift=-10,
                xanchor='center',  # Center align text
                yanchor='top'
            )
            # Labels for Rerun
            fig_combined.add_annotation(
                x=i+4,
                y=-0.1,
                text=metric,
                showarrow=False,
                font=dict(size=12, color='#000000', family='Arial Black'),
                yshift=-10,
                xanchor='center',  # Center align text
                yanchor='top'
            )
        
        st.plotly_chart(fig_combined, use_container_width=True)
    
    # Right column - Daily Engagement Trends
    with col2:
        # Date filter section - ADD THIS NEW SECTION
        # Create a container for the date filter buttons
        filter_container = st.container()
        date_filter_col1, date_filter_col2, date_filter_col3, date_filter_col4, date_filter_col5 = filter_container.columns(5)
        
        # Store the currently selected filter in session state
        if 'date_filter_selected' not in st.session_state:
            st.session_state.date_filter_selected = 'last7d'
        
        # Store custom date range in session state
        if 'custom_start_date' not in st.session_state:
            # Default to 7 days ago
            st.session_state.custom_start_date = (datetime.now() - timedelta(days=6)).date()
        
        if 'custom_end_date' not in st.session_state:
            # Default to today
            st.session_state.custom_end_date = datetime.now().date()
        
        # Current date for calculations
        today = datetime.now()
        
        # Date filter buttons with styling matching the dashboard
        filter_buttons_html = """
        <style>
        .date-filter-container {
            display: flex;
            gap: 8px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .date-filter-button {
            background-color: #722F37;
            color: #F5DEB3;
            border: none;
            border-radius: 5px;
            padding: 6px 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: center;
            flex-grow: 1;
            min-width: 60px;
        }
        .date-filter-button:hover {
            background-color: #8a3a45;
        }
        .date-filter-button.active {
            background-color: #8a3a45;
            border: 1px solid #F5DEB3;
        }
        </style>
        """
        
        st.markdown(filter_buttons_html, unsafe_allow_html=True)
        
        # Button selection logic
        with date_filter_col1:
            last7d_active = "active" if st.session_state.date_filter_selected == "last7d" else ""
            if st.button("Last 7d", key="last7d", use_container_width=True, 
                       help="View data from the last 7 days"):
                st.session_state.date_filter_selected = "last7d"
                
        with date_filter_col2:
            last30d_active = "active" if st.session_state.date_filter_selected == "last30d" else ""
            if st.button("Last 30d", key="last30d", use_container_width=True,
                       help="View data from the last 30 days"):
                st.session_state.date_filter_selected = "last30d"
                
        with date_filter_col3:
            lastQ_active = "active" if st.session_state.date_filter_selected == "lastQ" else ""
            if st.button("Last Q", key="lastQ", use_container_width=True,
                       help="View data from the last quarter"):
                st.session_state.date_filter_selected = "lastQ"
                
        with date_filter_col4:
            ytd_active = "active" if st.session_state.date_filter_selected == "ytd" else ""
            if st.button("YTD", key="ytd", use_container_width=True,
                       help="View data year to date"):
                st.session_state.date_filter_selected = "ytd"
                
        with date_filter_col5:
            custom_active = "active" if st.session_state.date_filter_selected == "custom" else ""
            if st.button("Custom", key="custom", use_container_width=True,
                       help="Select a custom date range"):
                st.session_state.date_filter_selected = "custom"
        
        # Show custom date selector if custom filter is selected
        if st.session_state.date_filter_selected == "custom":
            custom_col1, custom_col2 = st.columns(2)
            
            with custom_col1:
                selected_start = st.date_input(
                    "Start Date",
                    value=st.session_state.custom_start_date,
                    max_value=today
                )
                st.session_state.custom_start_date = selected_start
                
            with custom_col2:
                selected_end = st.date_input(
                    "End Date",
                    value=st.session_state.custom_end_date,
                    max_value=today
                )
                st.session_state.custom_end_date = selected_end

            # Validate date range
            if selected_start > selected_end:
                st.markdown('<p style="color:black;">Start date cannot be after end date. Please select a valid date range.</p>', unsafe_allow_html=True)
                # Swap the dates to fix the range
                st.session_state.custom_start_date = selected_end
                st.session_state.custom_end_date = selected_start
                # Use corrected dates
                start_date = datetime.combine(selected_end, datetime.min.time())
                end_date = datetime.combine(selected_start, datetime.max.time())
            else:
                start_date = datetime.combine(selected_start, datetime.min.time())
                end_date = datetime.combine(selected_end, datetime.max.time())
        
        # Calculate date range based on selected filter
        end_date = datetime.now().replace(hour=23, minute=59, second=59)
        
        if st.session_state.date_filter_selected == "last7d":
            start_date = (end_date - timedelta(days=6)).replace(hour=0, minute=0, second=0)
        elif st.session_state.date_filter_selected == "last30d":
            start_date = (end_date - timedelta(days=29)).replace(hour=0, minute=0, second=0)
        elif st.session_state.date_filter_selected == "lastQ":
            # Calculate start of the last quarter
            current_month = end_date.month
            quarter_month = ((current_month - 1) // 3) * 3 + 1  # Find start month of current quarter
            
            # If we're in the first month of a quarter (Jan/Apr/Jul/Oct)
            if quarter_month == current_month:
                # If January, go back to Q4 of previous year
                if current_month == 1:
                    start_date = datetime(end_date.year - 1, 10, 1)  # Q4 start (Oct 1)
                else:
                    start_date = datetime(end_date.year, quarter_month - 3, 1)  # Previous quarter start
            else:
                start_date = datetime(end_date.year, quarter_month, 1)  # Current quarter start

            # Example: If today is March 15, 2024
            # quarter_month would be 1 (Jan)
            # This would show Q1 2024 (Jan 1 - Mar 15)
            
            # If today is April 2, 2024
            # It would show Q1 2024 (Jan 1 - Mar 31)
        elif st.session_state.date_filter_selected == "ytd":
            start_date = datetime(end_date.year, 1, 1)
        else:  # custom
            start_date = datetime.combine(st.session_state.custom_start_date, datetime.min.time())
            end_date = datetime.combine(st.session_state.custom_end_date, datetime.max.time())
        
        # Get filtered time series data
        time_series_data = get_engagement_time_series_with_filter(start_date, end_date)

        if not time_series_data.empty:
            # Filter out zero values for x-axis display
            non_zero_data = time_series_data[time_series_data['engagements'] > 0]
            
            # Find maximum value
            max_value = time_series_data['engagements'].max()
            if max_value == 0:
                max_value = 1  # Prevent division by zero if no data
                
            # Calculate a proportional minimum value based on max_value
            fixed_min = -max_value * 0.05  # Just 5% of max value as padding below zero
            
            fig_trends = go.Figure()
            
            # Add the main trace
            fig_trends.add_trace(go.Scatter(
                x=time_series_data['date'],
                y=time_series_data['engagements'],
                mode='lines+markers+text',
                name='Engagements',
                line=dict(
                    color='#1DA1F2',
                    width=4,
                    shape='spline',
                    smoothing=1.3
                ),
                marker=dict(
                    size=[10 if val > 0 else 0 for val in time_series_data['engagements']],
                    color='#1DA1F2'
                ),
                text=[str(int(val)) if val > 0 else "" for val in time_series_data['engagements']],
                textposition='top center',
                textfont=dict(
                    size=14, 
                    color='#000000', 
                    family='Arial Black'
                ),
                showlegend=False
            ))

            fig_trends.update_layout(
                plot_bgcolor='#FAF3E0',
                paper_bgcolor='#FAF3E0',
                height=400,
                # Increase left and right margins to prevent label cropping
                margin=dict(l=60, r=60, t=30, b=60),
                yaxis=dict(
                    range=[fixed_min, max_value * 1.15],
                    showgrid=False,
                    showticklabels=True,
                    showline=True,
                    linewidth=1,
                    linecolor='black',
                    tickfont=dict(size=12, color='#000000', family='Arial Black'),
                    zeroline=True,
                    zerolinecolor='black',
                    zerolinewidth=1
                ),
                xaxis=dict(
                    showgrid=False,
                    showticklabels=True,
                    showline=True,
                    linewidth=1,
                    linecolor='black',
                    tickfont=dict(size=12, color='#000000', family='Arial Black'),
                    # Use non_zero_data for tick values
                    tickmode='array',
                    ticktext=[d.strftime("%b %d") for d in non_zero_data['date']],
                    tickvals=non_zero_data['date'],
                    range=[
                        start_date - timedelta(hours=12),  # Add padding to prevent label cropping
                        end_date + timedelta(hours=12)
                    ]
                )
            )

            # Special handling for Last 7 days
            if st.session_state.date_filter_selected == "last7d":
                # Ensure exactly 7 days
                end_date = datetime.now().replace(hour=23, minute=59, second=59)
                start_date = (end_date - timedelta(days=6)).replace(hour=0, minute=0, second=0)
                
                # Create array of all 7 dates regardless of data
                all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
                
                fig_trends.update_xaxes(
                    range=[
                        start_date - timedelta(hours=12),
                        end_date + timedelta(hours=12)
                    ],
                    tickmode='array',
                    ticktext=[d.strftime("%B %d") for d in all_dates],  # Changed to "March 14" format
                    tickvals=all_dates,
                    tickangle=0,  # Horizontal labels
                    tickfont=dict(size=10, color='#000000', family='Arial Black')  # Smaller font for longer labels
                )
            elif st.session_state.date_filter_selected == "last30d":
                # Ensure exactly 30 days
                end_date = datetime.now().replace(hour=23, minute=59, second=59)
                start_date = (end_date - timedelta(days=29)).replace(hour=0, minute=0, second=0)
                
                fig_trends.update_xaxes(
                    range=[
                        start_date - timedelta(hours=12),  # Start from exactly 30 days ago
                        end_date + timedelta(hours=12)
                    ],
                    showticklabels=False,  # Hide x-axis labels
                    showline=True,
                    linewidth=1,
                    linecolor='black'
                )
                
                # Update hover template to show full date
                fig_trends.update_traces(
                    hovertemplate="<b>%{x|%B %d}</b><br>" +
                                "Engagements: %{y}<br>" +
                                "<extra></extra>"
                )
            elif st.session_state.date_filter_selected == "lastQ":
                # Calculate start of the last quarter
                current_month = end_date.month
                quarter_month = ((current_month - 1) // 3) * 3 + 1  # Find start month of current quarter
                
                # If we're in the first month of a quarter (Jan/Apr/Jul/Oct)
                if quarter_month == current_month:
                    # If January, go back to Q4 of previous year
                    if current_month == 1:
                        start_date = datetime(end_date.year - 1, 10, 1)  # Q4 start (Oct 1)
                    else:
                        start_date = datetime(end_date.year, quarter_month - 3, 1)  # Previous quarter start
                else:
                    start_date = datetime(end_date.year, quarter_month, 1)  # Current quarter start

                # Example: If today is March 15, 2024
                # quarter_month would be 1 (Jan)
                # This would show Q1 2024 (Jan 1 - Mar 15)
                
                # If today is April 2, 2024
                # It would show Q1 2024 (Jan 1 - Mar 31)
                
                fig_trends.update_xaxes(
                    range=[
                        start_date - timedelta(hours=12),  # Start from beginning of quarter
                        end_date + timedelta(hours=12)
                    ],
                    showticklabels=False,  # Hide x-axis labels
                    showline=True,
                    linewidth=1,
                    linecolor='black'
                )
                
                # Update hover template to show full date
                fig_trends.update_traces(
                    hovertemplate="<b>%{x|%B %d}</b><br>" +
                                "Engagements: %{y}<br>" +
                                "<extra></extra>"  # Removes trace name from hover
                )
            elif st.session_state.date_filter_selected == "ytd":
                # YTD date range is already calculated (Jan 1 to current date)
                fig_trends.update_xaxes(
                    range=[
                        start_date - timedelta(hours=12),  # Start from Jan 1
                        end_date + timedelta(hours=12)
                    ],
                    showticklabels=False,  # Hide x-axis labels
                    showline=True,
                    linewidth=1,
                    linecolor='black'
                )
                
                # Update hover template to show full date
                fig_trends.update_traces(
                    hovertemplate="<b>%{x|%B %d}</b><br>" +
                                "Engagements: %{y}<br>" +
                                "<extra></extra>"
                )
            elif st.session_state.date_filter_selected == "custom":
                fig_trends.update_xaxes(
                    range=[
                        start_date - timedelta(hours=12),
                        end_date + timedelta(hours=12)
                    ],
                    showticklabels=False,  # Hide x-axis labels
                    showline=True,
                    linewidth=1,
                    linecolor='black'
                )
                
                # Update hover template to show full date
                fig_trends.update_traces(
                    hovertemplate="<b>%{x|%B %d}</b><br>" +
                                "Engagements: %{y}<br>" +
                                "<extra></extra>"
                )
            else:
                # For Last 30 days and other ranges
                fig_trends.update_xaxes(
                    range=[
                        non_zero_data['date'].min() - timedelta(hours=12),  # Align with first data point
                        non_zero_data['date'].max() + timedelta(hours=12)
                    ],
                    showticklabels=False,  # Hide x-axis labels
                    showline=True,
                    linewidth=1,
                    linecolor='black'
                )
                
                # Update hover template to show full date
                fig_trends.update_traces(
                    hovertemplate="<b>%{x|%B %d}</b><br>" +
                                  "Engagements: %{y}<br>" +
                                  "<extra></extra>"  # Removes trace name from hover
                )

            # Update layout for both cases
            fig_trends.update_layout(
                plot_bgcolor='#FAF3E0',
                paper_bgcolor='#FAF3E0',
                height=450, # Updated for DATA FILTER CHART & EVEN PURPSOE
                margin=dict(l=60, r=60, t=30, b=60),
                yaxis=dict(
                    range=[fixed_min, max_value * 1.15],
                    showgrid=False,
                    showticklabels=True,
                    showline=True,
                    linewidth=1,
                    linecolor='black',
                    tickfont=dict(size=12, color='#000000', family='Arial Black'),
                    zeroline=True,
                    zerolinecolor='black',
                    zerolinewidth=1
                ),
                width=None  # This allows the chart to use full container width
            )

            st.plotly_chart(fig_trends, use_container_width=True)
        else:
            st.debug("No data available for the selected date range.")

    # Create a single set of columns for both headers and charts
    col1, col2 = st.columns([1, 1])


    # For both Celebrity and User Engagements charts
    # Calculate maximum text width padding based on the values
    def get_max_text_padding(values):
        max_value = max(values)
        return max_value * 0.15  # 15% padding for text

    # Top 5 Celebrity Engagements
    with col1:
        # Add header
        st.markdown("""
            <div style="background: #722F37; padding: 15px; border-radius: 15px; margin: 20px 0;">
                <h2 style="color: #F5DEB3; font-size: 24px; margin: 0;">Top 5 Celebrity Engagements</h2>
            </div>
        """, unsafe_allow_html=True)

        if not celebrity_data.empty:
            # Sort in descending order by engagements
            celebrity_data = celebrity_data.sort_values('engagements', ascending=False)
            reversed_username_array = celebrity_data['username'].tolist()[::-1]
            
            # Calculate padding
            text_padding = get_max_text_padding(celebrity_data['engagements'])
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=celebrity_data['username'],
                x=celebrity_data['engagements'],
                orientation='h',
                marker_color='#3498db',
                text=celebrity_data['engagements'],
                textposition='outside',
                textfont=dict(size=14, color='#000000', family='Arial Black')
            ))
            
            fig.update_layout(
                plot_bgcolor='#FAF3E0',
                paper_bgcolor='#FAF3E0',
                height=450,
                margin=dict(l=20, r=100, t=20, b=20),  # Increased right margin
                showlegend=False,
                xaxis=dict(
                    range=[0, max(celebrity_data['engagements']) + text_padding],  # Add padding for text
                    showgrid=False,
                    showticklabels=True,
                    showline=True,
                    linewidth=1,
                    linecolor='black',
                    tickfont=dict(size=12, color='#000000', family='Arial Black')
                ),
                yaxis=dict(
                    categoryorder='array',
                    categoryarray=reversed_username_array,
                    showgrid=False,
                    showticklabels=True,
                    showline=True,
                    linewidth=1,
                    linecolor='black',
                    tickfont=dict(size=12, color='#000000', family='Arial Black')
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)

    # User Engagements - Column 2
    with col2:
        # Add header
        st.markdown("""
            <div style="background: #722F37; padding: 15px; border-radius: 15px; margin: 20px 0;">
                <h2 style="color: #F5DEB3; font-size: 24px; margin: 0;">Top 5 User Engagements</h2>
            </div>
        """, unsafe_allow_html=True)

        if not user_data.empty:
            # Sort in descending order by engagements
            user_data = user_data.sort_values('engagements', ascending=False)
            reversed_name_array = user_data['name'].tolist()[::-1]
            
            # Calculate padding
            text_padding = get_max_text_padding(user_data['engagements'])
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=user_data['name'],
                x=user_data['engagements'],
                orientation='h',
                marker_color='#3498db',
                text=user_data['engagements'],
                textposition='outside',
                textfont=dict(size=14, color='#000000', family='Arial Black')
            ))
            
            fig.update_layout(
                plot_bgcolor='#FAF3E0',
                paper_bgcolor='#FAF3E0',
                height=450,
                margin=dict(l=20, r=100, t=20, b=20),  # Increased right margin
                showlegend=False,
                xaxis=dict(
                    range=[0, max(user_data['engagements']) + text_padding],  # Add padding for text
                    showgrid=False,
                    showticklabels=True,
                    showline=True,
                    linewidth=1,
                    linecolor='black',
                    tickfont=dict(size=12, color='#000000', family='Arial Black')
                ),
                yaxis=dict(
                    categoryorder='array',
                    categoryarray=reversed_name_array,
                    showgrid=False,
                    showticklabels=True,
                    showline=True,
                    linewidth=1,
                    linecolor='black',
                    tickfont=dict(size=12, color='#000000', family='Arial Black')
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
