import streamlit as st
from datetime import datetime
import json
import os

def initialize_session_tracker():
    """Initialize the session tracker if it doesn't exist yet"""
    # Check if we need to initialize
    if "user_activities" not in st.session_state:
        st.session_state.user_activities = []
        
        # Try to load from disk if available
        try:
            # Path for temp storage - this is a workaround for session issues
            temp_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_session.json")
            if os.path.exists(temp_file):
                with open(temp_file, "r") as f:
                    data = json.load(f)
                    if "user_activities" in data and isinstance(data["user_activities"], list):
                        st.session_state.user_activities = data["user_activities"]
                        print(f"Loaded {len(st.session_state.user_activities)} activities from temp storage")
        except Exception as e:
            print(f"Failed to load session from disk: {e}")
    
    # Initialize policy content store if it doesn't exist
    if "policy_content" not in st.session_state:
        st.session_state.policy_content = {}
        
        # Try to load policy content from disk if available
        try:
            # Path for temp storage - this is a workaround for session issues
            temp_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_policy_content.json")
            if os.path.exists(temp_file):
                with open(temp_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        st.session_state.policy_content = data
                        print(f"Loaded {len(st.session_state.policy_content)} policy content items from temp storage")
        except Exception as e:
            print(f"Failed to load policy content from disk: {e}")

def track_activity(action, page_name, details=None):
    """Track a user activity in the session state
    
    Args:
        action (str): The action performed (e.g., "upload", "analyze", "compare")
        page_name (str): The name of the page where the action occurred
        details (dict, optional): Additional details about the action
    """
    initialize_session_tracker()
    
    activity = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "page": page_name,
        "details": details or {}
    }
    
    st.session_state.user_activities.append(activity)
    
    # Save to disk for persistence
    try:
        # Path for temp storage
        temp_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_session.json")
        with open(temp_file, "w") as f:
            json.dump({"user_activities": st.session_state.user_activities}, f)
            print(f"Saved {len(st.session_state.user_activities)} activities to temp storage")
    except Exception as e:
        print(f"Failed to save session to disk: {e}")

def store_policy_content(doc_id, content_type, content, summary=None, analysis=None):
    """Store policy document content and summaries
    
    Args:
        doc_id (str): Unique identifier for the document (name or generated ID)
        content_type (str): Type of content (e.g., "document", "comparison", "analysis")
        content (str): Raw content of the document or result
        summary (str, optional): A concise summary of the content
        analysis (str, optional): Analysis or recommendations
    """
    initialize_session_tracker()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    st.session_state.policy_content[doc_id] = {
        "type": content_type,
        "content": content,
        "summary": summary,
        "analysis": analysis,
        "timestamp": timestamp
    }
    
    # Save to disk for persistence
    try:
        # Path for temp storage
        temp_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_policy_content.json")
        with open(temp_file, "w") as f:
            json.dump(st.session_state.policy_content, f)
            print(f"Saved {len(st.session_state.policy_content)} policy content items to temp storage")
    except Exception as e:
        print(f"Failed to save policy content to disk: {e}")

def get_session_summary():
    """Generate a human-readable summary of the user's session activities
    
    Returns:
        str: A formatted text summary of the user's activities
    """
    initialize_session_tracker()
    
    if not st.session_state.user_activities:
        return "You haven't performed any actions in this session yet."
    
    # Group activities by page
    page_activities = {}
    for activity in st.session_state.user_activities:
        page = activity["page"]
        if page not in page_activities:
            page_activities[page] = []
        page_activities[page].append(activity)
    
    # Count total activities
    total_activities = len(st.session_state.user_activities)
    
    # Get earliest and latest timestamps
    timestamps = [datetime.strptime(a["timestamp"], "%Y-%m-%d %H:%M:%S") for a in st.session_state.user_activities]
    earliest = min(timestamps).strftime("%I:%M %p")
    latest = max(timestamps).strftime("%I:%M %p")
    
    # Generate summary text - start with an overview
    summary = f"Session Summary: You've performed {total_activities} actions between {earliest} and {latest}.\n\n"
    
    # Add a summary by page
    for page, activities in page_activities.items():
        page_count = len(activities)
        summary += f"On the {page} page, you performed {page_count} actions.\n"
        
        # Group similar activities within each page
        action_groups = {}
        for activity in activities:
            action = activity["action"]
            if action not in action_groups:
                action_groups[action] = []
            action_groups[action].append(activity)
        
        # Summarize each action group
        for action, action_activities in action_groups.items():
            if len(action_activities) == 1:
                # Single activity
                activity = action_activities[0]
                time = activity["timestamp"].split()[1][:5]  # Just HH:MM
                
                summary_line = f"- At {time}, you {action}"
                
                # Add details if they exist
                details = activity["details"]
                if details:
                    if "document_name" in details:
                        summary_line += f" document '{details['document_name']}'"
                    if "query" in details:
                        summary_line += f" with the query '{details['query']}'"
                    if "legislator_name" in details:
                        summary_line += f" '{details['legislator_name']}'"
                    if "report_title" in details:
                        summary_line += f" titled '{details['report_title']}'"
                    if "zip_code" in details:
                        summary_line += f" for ZIP code {details['zip_code']}"
                    if "result" in details:
                        summary_line += f" and received a {details['result']}"
                
                summary += summary_line + ".\n"
            else:
                # Multiple similar activities
                count = len(action_activities)
                first_time = action_activities[0]["timestamp"].split()[1][:5]  # Just HH:MM of first activity
                last_time = action_activities[-1]["timestamp"].split()[1][:5]  # Just HH:MM of last activity
                
                # Extract common details if available
                examples = []
                for i, activity in enumerate(action_activities):
                    details = activity["details"]
                    if details and i < 3:  # Limit to 3 examples
                        if "document_name" in details:
                            examples.append(details["document_name"])
                        elif "legislator_name" in details:
                            examples.append(details["legislator_name"])
                        elif "report_title" in details:
                            examples.append(details["report_title"])
                
                summary_line = f"- Between {first_time} and {last_time}, you {action} {count} times"
                
                if examples:
                    examples_str = ", ".join([f"'{ex}'" for ex in examples])
                    if len(examples) < len(action_activities):
                        examples_str += f", and {len(action_activities) - len(examples)} others"
                    summary_line += f" including {examples_str}"
                
                summary += summary_line + ".\n"
        
        summary += "\n"
    
    # Add a conclusion
    most_active_page = max(page_activities.items(), key=lambda x: len(x[1]))[0]
    summary += f"You were most active on the {most_active_page} page. "
    
    # Add personalized suggestions based on activity
    if "Impact Simulator" in page_activities and "Export Report" not in page_activities:
        summary += "You might want to export your impact simulation results using the Export Report page."
    elif "Decoder" in page_activities and "Compare Bills" not in page_activities:
        summary += "You might want to try comparing different policy documents using the Compare Bills page."
    elif "Chat Memory" in page_activities and "Voice Summary" not in page_activities:
        summary += "You can create an audio summary of your chat session using this Voice Summary page."
    
    return summary

def get_policy_content_summary():
    """Generate a summary of policy content from the session
    
    Returns:
        str: A formatted summary of policy documents and analysis
    """
    initialize_session_tracker()
    
    if not st.session_state.policy_content:
        return "No policy documents have been analyzed in this session yet."
    
    # Create plain text summary instead of Markdown
    summary = "Policy Content Summary:\n\n"
    
    # Group policy content by type
    content_by_type = {}
    for doc_id, data in st.session_state.policy_content.items():
        content_type = data["type"]
        if content_type not in content_by_type:
            content_by_type[content_type] = []
        content_by_type[content_type].append((doc_id, data))
    
    # Function to convert abbreviations to full words and handle acronyms
    def expand_abbreviations(text):
        # Common abbreviations to expand
        replacements = {
            "vs.": "versus",
            "vs": "versus",
            "e.g.": "for example",
            "i.e.": "that is",
            "etc.": "etcetera",
            "approx.": "approximately",
            "U.S.": "United States",
            "U.S.A.": "United States of America",
            "U.K.": "United Kingdom",
            "%": "percent",
            "ZIP": "zip code",
            "&": "and",
            "$": "dollars",
            "#": "number",
            "w/": "with",
            "w/o": "without",
            "govt.": "government",
            "govt": "government",
            "admin.": "administration",
            "admin": "administration"
        }
        
        # Handle common acronyms by adding spaces between letters
        # This makes TTS read it as letters instead of as a word
        def process_acronyms(match):
            acronym = match.group(0)
            # First check if it's in our exceptions list (acronyms to keep as-is)
            keep_as_is = ["NASA", "COVID", "AIDS", "NATO"]
            if acronym in keep_as_is:
                return acronym
                
            # Otherwise add spaces
            return " ".join(acronym)
        
        # First replace common abbreviations
        for abbr, full in replacements.items():
            text = text.replace(abbr, full)
            
        # Process acronyms in parentheses - a common pattern: "Something Name (SN)"
        import re
        # Find patterns like "Something (ACRONYM)" and add the word "acronym" after it
        acronym_pattern = r'\(([A-Z]{2,})\)'
        text = re.sub(acronym_pattern, r'(acronym \1)', text)
            
        return text
    
    # Summarize each content type
    for content_type, items in content_by_type.items():
        # Sort by timestamp (newest first)
        sorted_items = sorted(items, key=lambda x: x[1]["timestamp"], reverse=True)
        
        # Add content type as a section header (plain text, not Markdown)
        summary += f"{content_type.title()} Section\n\n"
        
        for i, (doc_id, data) in enumerate(sorted_items):
            # Extract timestamp but skip document name in output
            timestamp = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S").strftime("%I:%M %p")
            
            # Use a simpler identifier instead of the filename
            summary += f"Item {i+1}. Analyzed at {timestamp}\n"
            
            # Add summary if available
            if data.get("summary"):
                # Clean up the summary for TTS
                clean_summary = expand_abbreviations(data["summary"])
                summary += f"Summary: {clean_summary}\n\n"
            
            # Add analysis/recommendations if available
            if data.get("analysis"):
                # Clean up the analysis for TTS
                clean_analysis = expand_abbreviations(data["analysis"])
                summary += f"Analysis and Recommendations: {clean_analysis}\n\n"
        
        summary += "\n"
    
    # Add general recommendations based on content as plain text
    summary += "General Recommendations Section\n\n"
    
    if "comparison" in content_by_type:
        summary += "Based on the bill comparisons you've performed, consider focusing on the key differences in policy approaches and how they might impact implementation.\n\n"
    
    if "document" in content_by_type:
        summary += "For documents you've analyzed, consider exploring related legislation or research reports to gain a more comprehensive understanding of the policy landscape.\n\n"
    
    if "analysis" in content_by_type:
        summary += "The analyses you've reviewed suggest several avenues for further research, particularly regarding implementation feasibility and stakeholder impacts.\n\n"
    
    return summary

def clear_session_activities():
    """Clear all tracked activities in the current session"""
    if "user_activities" in st.session_state:
        st.session_state.user_activities = []
        
        # Clear disk storage as well
        try:
            temp_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_session.json")
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print("Removed temp session storage file")
        except Exception as e:
            print(f"Failed to remove temp session file: {e}")
    
    if "policy_content" in st.session_state:
        st.session_state.policy_content = {}
        
        # Clear disk storage as well
        try:
            temp_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_policy_content.json")
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print("Removed temp policy content storage file")
        except Exception as e:
            print(f"Failed to remove temp policy content file: {e}") 