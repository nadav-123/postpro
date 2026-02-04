"""
PostPro V1.5 - The Reputation Guardian
LinkedIn Post Analyzer & Optimizer

A tool that compares your new draft against your proven history
to ensure authenticity and strategic alignment.
"""

import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
from io import BytesIO

# Page config
st.set_page_config(
    page_title="PostPro - LinkedIn Post Optimizer",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0077B5;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-top: 0;
    }
    .score-high { color: #28a745; font-size: 3rem; font-weight: bold; }
    .score-medium { color: #ffc107; font-size: 3rem; font-weight: bold; }
    .score-low { color: #dc3545; font-size: 3rem; font-weight: bold; }
    .risk-low { background-color: #d4edda; padding: 10px; border-radius: 5px; }
    .risk-medium { background-color: #fff3cd; padding: 10px; border-radius: 5px; }
    .risk-high { background-color: #f8d7da; padding: 10px; border-radius: 5px; }
    .stTextArea textarea { font-size: 14px; }
</style>
""", unsafe_allow_html=True)


def parse_linkedin_xlsx(uploaded_file) -> dict:
    """
    Parse LinkedIn Content export XLSX file.
    Returns dict with top_posts_by_engagement and top_posts_by_impressions.
    """
    try:
        xlsx = pd.ExcelFile(BytesIO(uploaded_file.read()))
        
        # Read TOP POSTS sheet
        df = pd.read_excel(xlsx, sheet_name='TOP POSTS', header=None)
        
        # Find the header row (contains 'Post URL')
        header_row = None
        for idx, row in df.iterrows():
            if 'Post URL' in row.values:
                header_row = idx
                break
        
        if header_row is None:
            return {"error": "Could not find Post URL header in file"}
        
        # The file has two tables side by side:
        # Columns 0-2: By Engagements (URL, Date, Engagements)
        # Columns 4-6: By Impressions (URL, Date, Impressions)
        
        # Extract engagement table
        engagement_df = df.iloc[header_row+1:, 0:3].copy()
        engagement_df.columns = ['url', 'date', 'engagements']
        engagement_df = engagement_df.dropna(subset=['url'])
        engagement_df = engagement_df[engagement_df['url'].str.contains('linkedin.com', na=False)]
        
        # Extract impressions table
        impressions_df = df.iloc[header_row+1:, 4:7].copy()
        impressions_df.columns = ['url', 'date', 'impressions']
        impressions_df = impressions_df.dropna(subset=['url'])
        impressions_df = impressions_df[impressions_df['url'].str.contains('linkedin.com', na=False)]
        
        # Also try to get demographics
        demographics = {}
        try:
            demo_df = pd.read_excel(xlsx, sheet_name='DEMOGRAPHICS')
            top_titles = demo_df[demo_df['Top Demographics'] == 'Job titles'].head(5)
            demographics = top_titles[['Value', 'Percentage']].to_dict('records')
        except:
            pass
        
        return {
            "top_by_engagement": engagement_df.head(10).to_dict('records'),
            "top_by_impressions": impressions_df.head(10).to_dict('records'),
            "demographics": demographics
        }
        
    except Exception as e:
        return {"error": str(e)}


def analyze_posts(anchor: str, draft: str, api_key: str) -> dict:
    """
    Send anchor and draft to Google Gemini for comparison analysis.
    Returns structured analysis result.
    """
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""You are a Strategic LinkedIn Editor for a Senior Executive.
Your task is to validate if the [New Draft] matches the DNA of the [Anchor Post].

CONTEXT:
The user's audience consists of senior professionals - Founders, CEOs, and executives.

FATAL ERRORS to flag:
1. "Junior" advice (basic tips that sound inexperienced)
2. "Bot Speak" (words like: delve, landscape, unlock, game-changer, leverage, synergy)
3. "Wall of Text" (paragraphs > 3 lines without breaks)
4. Tone mismatch (formal vs casual, story vs data)

ANALYSIS FRAMEWORK:
1. Visual Physics: Line breaks, paragraph density, white space, overall structure
2. Tonal DNA: Cynicism vs Optimism, Direct vs Storytelling, Personal vs Professional
3. Hook Geometry: Does the first sentence create similar psychological impact?
4. Authority Level: Does it sound like the same seniority level?

[ANCHOR POST - This performed well]:
{anchor}

---

[NEW DRAFT - Analyze this]:
{draft}

Compare the draft to the anchor and provide your analysis.

OUTPUT: Return ONLY valid JSON (no markdown, no explanation before/after, no ```json tags):
{{
    "score": <number 0-100>,
    "verdict": "<one sentence explaining the main gap>",
    "risk_level": "<Low/Medium/High>",
    "analysis": {{
        "visual_physics": "<brief assessment>",
        "tonal_dna": "<brief assessment>",
        "hook_comparison": "<brief assessment>"
    }},
    "fatal_errors": ["<list any fatal errors found, empty array if none>"],
    "fix_suggestions": ["<specific actionable suggestion 1>", "<suggestion 2>", "<suggestion 3>"],
    "rewritten_hook": "<rewritten first 2-3 lines that match anchor's style>"
}}"""

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Clean up potential markdown formatting
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()
        
        return json.loads(result_text)
        
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response: {str(e)}", "raw": result_text}
    except Exception as e:
        return {"error": str(e)}


# ============== MAIN APP ==============

st.markdown('<p class="main-header">🛡️ PostPro</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">The Reputation Guardian - Validate your LinkedIn posts before publishing</p>', unsafe_allow_html=True)

st.divider()

# Sidebar for API key and file upload
with st.sidebar:
    st.header("⚙️ Setup")
    
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        help="Your Google Gemini API key for AI analysis"
    )
    
    st.divider()
    
    st.header("📊 Import Your Data")
    uploaded_file = st.file_uploader(
        "Upload LinkedIn Content Export (XLSX)",
        type=['xlsx'],
        help="Download from LinkedIn: Settings → Get a copy of your data → Posts"
    )
    
    if uploaded_file:
        with st.spinner("Parsing your LinkedIn data..."):
            parsed_data = parse_linkedin_xlsx(uploaded_file)
        
        if "error" in parsed_data:
            st.error(f"Error parsing file: {parsed_data['error']}")
        else:
            st.success("✅ Data loaded successfully!")
            
            # Show demographics if available
            if parsed_data.get("demographics"):
                st.subheader("Your Audience")
                for demo in parsed_data["demographics"][:3]:
                    pct = float(demo['Percentage']) * 100
                    st.write(f"• {demo['Value']}: {pct:.1f}%")
            
            # Store in session state
            st.session_state['parsed_data'] = parsed_data

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Anchor Post (Your Proven Winner)")
    
    # If we have parsed data, show selector
    if 'parsed_data' in st.session_state and not st.session_state['parsed_data'].get('error'):
        data = st.session_state['parsed_data']
        
        with st.expander("📈 Your Top Posts (click URL, copy text, paste below)"):
            st.write("**By Engagement:**")
            for i, post in enumerate(data['top_by_engagement'][:5], 1):
                eng = post.get('engagements', 'N/A')
                st.markdown(f"{i}. [{post['url'][:50]}...]({post['url']}) - {eng} engagements")
            
            st.write("**By Impressions:**")
            for i, post in enumerate(data['top_by_impressions'][:5], 1):
                imp = post.get('impressions', 'N/A')
                st.markdown(f"{i}. [{post['url'][:50]}...]({post['url']}) - {imp:,} impressions")
    
    anchor_text = st.text_area(
        "Paste your best-performing post here",
        height=250,
        placeholder="Paste the full text of a LinkedIn post that performed well for you...\n\nThis will be your 'DNA template' - the style and structure that resonates with your audience."
    )

with col2:
    st.subheader("📝 New Draft (To Analyze)")
    
    draft_text = st.text_area(
        "Paste your new draft here",
        height=250,
        placeholder="Paste the new post you want to publish...\n\nWe'll compare it to your anchor and tell you if it matches your winning formula."
    )

st.divider()

# Analysis button
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn2:
    analyze_button = st.button(
        "🔍 Run DNA Analysis",
        type="primary",
        use_container_width=True,
        disabled=not (api_key and anchor_text and draft_text)
    )

if not api_key:
    st.info("👈 Enter your Google Gemini API key in the sidebar to enable analysis")
elif not anchor_text or not draft_text:
    st.info("✍️ Paste both an anchor post and a new draft to analyze")

# Run analysis
if analyze_button and api_key and anchor_text and draft_text:
    with st.spinner("🧠 Analyzing your posts..."):
        result = analyze_posts(anchor_text, draft_text, api_key)
    
    if "error" in result:
        st.error(f"Analysis failed: {result['error']}")
        if "raw" in result:
            with st.expander("Raw response"):
                st.code(result['raw'])
    else:
        st.divider()
        st.header("📊 Analysis Results")
        
        # Score and Risk display
        res_col1, res_col2, res_col3 = st.columns(3)
        
        with res_col1:
            score = result.get('score', 0)
            score_class = 'score-high' if score >= 70 else 'score-medium' if score >= 40 else 'score-low'
            st.markdown(f"**Humanity Score**")
            st.markdown(f'<p class="{score_class}">{score}/100</p>', unsafe_allow_html=True)
        
        with res_col2:
            risk = result.get('risk_level', 'Unknown')
            risk_class = 'risk-low' if risk == 'Low' else 'risk-medium' if risk == 'Medium' else 'risk-high'
            st.markdown(f"**Risk Level**")
            st.markdown(f'<div class="{risk_class}"><strong>{risk}</strong></div>', unsafe_allow_html=True)
        
        with res_col3:
            st.markdown("**Verdict**")
            st.write(result.get('verdict', 'No verdict available'))
        
        st.divider()
        
        # Detailed analysis
        analysis_col1, analysis_col2 = st.columns(2)
        
        with analysis_col1:
            st.subheader("🔬 Detailed Analysis")
            analysis = result.get('analysis', {})
            
            st.markdown("**Visual Physics:**")
            st.write(analysis.get('visual_physics', 'N/A'))
            
            st.markdown("**Tonal DNA:**")
            st.write(analysis.get('tonal_dna', 'N/A'))
            
            st.markdown("**Hook Comparison:**")
            st.write(analysis.get('hook_comparison', 'N/A'))
            
            # Fatal errors
            fatal_errors = result.get('fatal_errors', [])
            if fatal_errors:
                st.markdown("**⚠️ Fatal Errors Detected:**")
                for error in fatal_errors:
                    st.error(error)
        
        with analysis_col2:
            st.subheader("💡 Recommendations")
            
            suggestions = result.get('fix_suggestions', [])
            for i, suggestion in enumerate(suggestions, 1):
                st.markdown(f"{i}. {suggestion}")
            
            st.divider()
            
            st.subheader("✨ Suggested Hook Rewrite")
            rewritten = result.get('rewritten_hook', '')
            if rewritten:
                st.success(rewritten)
                st.button("📋 Copy to clipboard", key="copy_hook")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    Built by Nadav Druker | PostPro V1.5 - The Reputation Guardian
</div>
""", unsafe_allow_html=True)
