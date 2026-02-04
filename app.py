"""
PostPro V2.0 - The Reputation Guardian
LinkedIn Post Analyzer & Optimizer
Beautiful UI with Dashboard & Statistics
"""

import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
from io import BytesIO
from datetime import datetime

# Page config
st.set_page_config(
    page_title="PostPro - LinkedIn Post Optimizer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS with gradients and animations
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0;
    }
    
    .sub-header {
        color: #a0aec0;
        font-size: 1.1rem;
        text-align: center;
        margin-top: 5px;
        margin-bottom: 30px;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(145deg, #1e2a4a 0%, #152238 100%);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(102, 126, 234, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #a0aec0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 8px;
    }
    
    /* Score display */
    .score-container {
        background: linear-gradient(145deg, #1e2a4a 0%, #152238 100%);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        border: 2px solid;
        animation: pulse 2s infinite;
    }
    
    .score-high {
        border-color: #48bb78;
        box-shadow: 0 0 30px rgba(72, 187, 120, 0.3);
    }
    
    .score-medium {
        border-color: #ecc94b;
        box-shadow: 0 0 30px rgba(236, 201, 75, 0.3);
    }
    
    .score-low {
        border-color: #fc8181;
        box-shadow: 0 0 30px rgba(252, 129, 129, 0.3);
    }
    
    .score-number {
        font-size: 4rem;
        font-weight: 700;
    }
    
    .score-number.high { color: #48bb78; }
    .score-number.medium { color: #ecc94b; }
    .score-number.low { color: #fc8181; }
    
    /* Risk badges */
    .risk-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .risk-low {
        background: linear-gradient(90deg, #48bb78 0%, #38a169 100%);
        color: white;
    }
    
    .risk-medium {
        background: linear-gradient(90deg, #ecc94b 0%, #d69e2e 100%);
        color: #1a1a2e;
    }
    
    .risk-high {
        background: linear-gradient(90deg, #fc8181 0%, #e53e3e 100%);
        color: white;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Text area styling */
    .stTextArea textarea {
        background: #1e2a4a;
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        color: #e2e8f0;
        font-size: 15px;
        padding: 15px;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e2a4a 0%, #152238 100%);
    }
    
    [data-testid="stSidebar"] .stTextInput input {
        background: #0f172a;
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 8px;
        color: #e2e8f0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #1e2a4a;
        border-radius: 10px;
        color: #a0aec0;
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #1e2a4a;
        border-radius: 10px;
        color: #e2e8f0;
    }
    
    /* Analysis results cards */
    .analysis-card {
        background: linear-gradient(145deg, #1e2a4a 0%, #152238 100%);
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
    
    .suggestion-item {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin: 8px 0;
        border-left: 3px solid #667eea;
        color: #e2e8f0;
    }
    
    .hook-rewrite {
        background: linear-gradient(145deg, rgba(72, 187, 120, 0.1) 0%, rgba(56, 161, 105, 0.1) 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(72, 187, 120, 0.3);
        color: #48bb78;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #4a5568;
        padding: 30px;
        margin-top: 50px;
    }
    
    /* Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-in {
        animation: slideIn 0.5s ease forwards;
    }
    
    /* Mobile preview */
    .mobile-preview {
        background: #000;
        border-radius: 30px;
        padding: 20px;
        max-width: 320px;
        margin: 0 auto;
        border: 3px solid #333;
    }
    
    .mobile-header {
        background: #1a1a1a;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    
    .mobile-content {
        background: #fff;
        color: #000;
        padding: 15px;
        border-radius: 10px;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .see-more {
        color: #0a66c2;
        font-weight: 600;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom divider */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 30px 0;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'total_analyses' not in st.session_state:
    st.session_state.total_analyses = 0
if 'avg_score' not in st.session_state:
    st.session_state.avg_score = 0


def parse_linkedin_xlsx(uploaded_file) -> dict:
    """Parse LinkedIn Content export XLSX file."""
    try:
        xlsx = pd.ExcelFile(BytesIO(uploaded_file.read()))
        df = pd.read_excel(xlsx, sheet_name='TOP POSTS', header=None)
        
        header_row = None
        for idx, row in df.iterrows():
            if 'Post URL' in row.values:
                header_row = idx
                break
        
        if header_row is None:
            return {"error": "Could not find Post URL header in file"}
        
        engagement_df = df.iloc[header_row+1:, 0:3].copy()
        engagement_df.columns = ['url', 'date', 'engagements']
        engagement_df = engagement_df.dropna(subset=['url'])
        engagement_df = engagement_df[engagement_df['url'].str.contains('linkedin.com', na=False)]
        
        impressions_df = df.iloc[header_row+1:, 4:7].copy()
        impressions_df.columns = ['url', 'date', 'impressions']
        impressions_df = impressions_df.dropna(subset=['url'])
        impressions_df = impressions_df[impressions_df['url'].str.contains('linkedin.com', na=False)]
        
        demographics = {}
        try:
            demo_df = pd.read_excel(xlsx, sheet_name='DEMOGRAPHICS')
            top_titles = demo_df[demo_df['Top Demographics'] == 'Job titles'].head(5)
            demographics = top_titles[['Value', 'Percentage']].to_dict('records')
        except:
            pass
        
        # Get engagement trends
        try:
            trend_df = pd.read_excel(xlsx, sheet_name='ENGAGEMENT')
            trends = trend_df.to_dict('records')
        except:
            trends = []
        
        return {
            "top_by_engagement": engagement_df.head(10).to_dict('records'),
            "top_by_impressions": impressions_df.head(10).to_dict('records'),
            "demographics": demographics,
            "trends": trends
        }
        
    except Exception as e:
        return {"error": str(e)}


def analyze_posts(anchor: str, draft: str, api_key: str) -> dict:
    """Send anchor and draft to Google Gemini for comparison analysis."""
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
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


def render_mobile_preview(text: str, char_limit: int = 150):
    """Render a mobile-style preview with See More cutoff."""
    lines = text.split('\n')
    preview_lines = []
    char_count = 0
    line_count = 0
    cut_off = False
    
    for line in lines:
        if line_count >= 3 or char_count >= char_limit:
            cut_off = True
            break
        preview_lines.append(line)
        char_count += len(line)
        line_count += 1
    
    preview_text = '\n'.join(preview_lines)
    if cut_off:
        preview_text += '...'
    
    return preview_text, cut_off


# ============== MAIN APP ==============

# Header
st.markdown('<h1 class="main-header">🛡️ PostPro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">The Reputation Guardian - AI-Powered LinkedIn Post Optimizer</p>', unsafe_allow_html=True)
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    api_key = st.text_input(
        "🔑 Gemini API Key",
        type="password",
        help="Get your free API key from aistudio.google.com"
    )
    
    st.markdown("---")
    
    st.markdown("### 📊 Import LinkedIn Data")
    uploaded_file = st.file_uploader(
        "Upload Content Export (XLSX)",
        type=['xlsx'],
        help="Settings → Get a copy of your data → Posts"
    )
    
    if uploaded_file:
        with st.spinner("📈 Analyzing your data..."):
            parsed_data = parse_linkedin_xlsx(uploaded_file)
        
        if "error" not in parsed_data:
            st.success("✅ Data loaded!")
            st.session_state['parsed_data'] = parsed_data
            
            if parsed_data.get("demographics"):
                st.markdown("#### 👥 Your Audience")
                for demo in parsed_data["demographics"][:3]:
                    pct = float(demo['Percentage']) * 100
                    st.markdown(f"• **{demo['Value']}**: {pct:.1f}%")

# Main content with tabs
tab1, tab2, tab3 = st.tabs(["🎯 Analyzer", "📈 Dashboard", "📚 Library"])

# TAB 1: Analyzer
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Anchor Post")
        st.markdown("*Your proven winner - the DNA template*")
        
        if 'parsed_data' in st.session_state:
            with st.expander("📈 Your Top Posts"):
                data = st.session_state['parsed_data']
                for i, post in enumerate(data['top_by_engagement'][:3], 1):
                    eng = post.get('engagements', 'N/A')
                    st.markdown(f"**{i}.** [{eng} engagements]({post['url']})")
        
        anchor_text = st.text_area(
            "Paste your best post",
            height=200,
            placeholder="Paste a LinkedIn post that performed well...",
            key="anchor"
        )
    
    with col2:
        st.markdown("### 📝 New Draft")
        st.markdown("*Your post to analyze*")
        
        draft_text = st.text_area(
            "Paste your draft",
            height=200,
            placeholder="Paste the new post you want to publish...",
            key="draft"
        )
        
        # Mobile preview
        if draft_text:
            st.markdown("#### 📱 Mobile Preview")
            preview, is_cut = render_mobile_preview(draft_text)
            preview_html = f"""
            <div style="background: #fff; color: #000; padding: 15px; border-radius: 10px; 
                        font-size: 14px; line-height: 1.5; max-width: 300px; border: 2px solid #e2e8f0;">
                {preview.replace(chr(10), '<br>')}
                {'<span style="color: #0a66c2; font-weight: 600;">...see more</span>' if is_cut else ''}
            </div>
            """
            st.markdown(preview_html, unsafe_allow_html=True)
            if is_cut:
                st.warning("⚠️ Hook cuts off before main message!")

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Analyze button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        analyze_btn = st.button(
            "🚀 Run DNA Analysis",
            use_container_width=True,
            disabled=not (api_key and anchor_text and draft_text)
        )
    
    if not api_key:
        st.info("👈 Enter your Gemini API key in the sidebar")
    
    # Results
    if analyze_btn and api_key and anchor_text and draft_text:
        with st.spinner("🧠 Analyzing your DNA..."):
            result = analyze_posts(anchor_text, draft_text, api_key)
        
        if "error" in result:
            st.error(f"❌ {result['error']}")
        else:
            # Update stats
            st.session_state.total_analyses += 1
            st.session_state.analysis_history.append({
                'score': result.get('score', 0),
                'timestamp': datetime.now().isoformat()
            })
            scores = [h['score'] for h in st.session_state.analysis_history]
            st.session_state.avg_score = sum(scores) / len(scores)
            
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            st.markdown("## 📊 Analysis Results")
            
            # Score and Risk
            res_col1, res_col2, res_col3 = st.columns(3)
            
            with res_col1:
                score = result.get('score', 0)
                score_class = 'high' if score >= 70 else 'medium' if score >= 40 else 'low'
                st.markdown(f"""
                <div class="score-container score-{score_class}">
                    <div class="score-number {score_class}">{score}</div>
                    <div style="color: #a0aec0; font-size: 1.2rem;">Humanity Score</div>
                </div>
                """, unsafe_allow_html=True)
            
            with res_col2:
                risk = result.get('risk_level', 'Unknown')
                risk_class = risk.lower()
                st.markdown(f"""
                <div class="metric-card" style="text-align: center; padding-top: 40px;">
                    <div class="risk-badge risk-{risk_class}">{risk} Risk</div>
                    <div style="color: #a0aec0; margin-top: 20px;">Reputation Risk Level</div>
                </div>
                """, unsafe_allow_html=True)
            
            with res_col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="color: #667eea; font-weight: 600; margin-bottom: 10px;">📋 Verdict</div>
                    <div style="color: #e2e8f0; font-size: 1rem; line-height: 1.6;">
                        {result.get('verdict', 'No verdict available')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Detailed analysis
            detail_col1, detail_col2 = st.columns(2)
            
            with detail_col1:
                st.markdown("### 🔬 Analysis Breakdown")
                analysis = result.get('analysis', {})
                
                st.markdown(f"""
                <div class="analysis-card">
                    <strong style="color: #667eea;">📐 Visual Physics</strong><br>
                    <span style="color: #e2e8f0;">{analysis.get('visual_physics', 'N/A')}</span>
                </div>
                <div class="analysis-card">
                    <strong style="color: #667eea;">🎭 Tonal DNA</strong><br>
                    <span style="color: #e2e8f0;">{analysis.get('tonal_dna', 'N/A')}</span>
                </div>
                <div class="analysis-card">
                    <strong style="color: #667eea;">🎣 Hook Comparison</strong><br>
                    <span style="color: #e2e8f0;">{analysis.get('hook_comparison', 'N/A')}</span>
                </div>
                """, unsafe_allow_html=True)
                
                fatal_errors = result.get('fatal_errors', [])
                if fatal_errors and fatal_errors[0]:
                    st.markdown("### ⚠️ Fatal Errors")
                    for error in fatal_errors:
                        st.error(error)
            
            with detail_col2:
                st.markdown("### 💡 Recommendations")
                suggestions = result.get('fix_suggestions', [])
                for i, suggestion in enumerate(suggestions, 1):
                    st.markdown(f"""
                    <div class="suggestion-item">
                        <strong>{i}.</strong> {suggestion}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("### ✨ Suggested Hook Rewrite")
                rewritten = result.get('rewritten_hook', '')
                if rewritten:
                    st.markdown(f"""
                    <div class="hook-rewrite">
                        {rewritten}
                    </div>
                    """, unsafe_allow_html=True)

# TAB 2: Dashboard
with tab2:
    st.markdown("### 📈 Performance Dashboard")
    
    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.total_analyses}</div>
            <div class="metric-label">Total Analyses</div>
        </div>
        """, unsafe_allow_html=True)
    
    with m2:
        avg = round(st.session_state.avg_score, 1)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg}</div>
            <div class="metric-label">Avg Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with m3:
        high_scores = len([h for h in st.session_state.analysis_history if h['score'] >= 70])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{high_scores}</div>
            <div class="metric-label">High Scores (70+)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with m4:
        if 'parsed_data' in st.session_state:
            top_eng = st.session_state['parsed_data']['top_by_engagement']
            if top_eng:
                best = top_eng[0].get('engagements', 0)
            else:
                best = 0
        else:
            best = 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{best}</div>
            <div class="metric-label">Best Engagement</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Score history chart
    if st.session_state.analysis_history:
        st.markdown("### 📊 Score History")
        history_df = pd.DataFrame(st.session_state.analysis_history)
        history_df['index'] = range(1, len(history_df) + 1)
        st.line_chart(history_df.set_index('index')['score'])
    
    # LinkedIn trends
    if 'parsed_data' in st.session_state and st.session_state['parsed_data'].get('trends'):
        st.markdown("### 📈 LinkedIn Engagement Trends")
        trends = st.session_state['parsed_data']['trends']
        if trends:
            trend_df = pd.DataFrame(trends)
            if 'Date' in trend_df.columns and 'Impressions' in trend_df.columns:
                trend_df['Date'] = pd.to_datetime(trend_df['Date'])
                st.line_chart(trend_df.set_index('Date')['Impressions'])

# TAB 3: Library
with tab3:
    st.markdown("### 📚 Anchor Library")
    st.markdown("*Save your best posts as templates for future analysis*")
    
    st.info("🚧 Coming in V2.1: Save and manage your anchor posts in a local database!")
    
    if 'parsed_data' in st.session_state:
        st.markdown("### 🏆 Your Top Performing Posts")
        data = st.session_state['parsed_data']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### By Engagement")
            for i, post in enumerate(data['top_by_engagement'][:5], 1):
                eng = post.get('engagements', 'N/A')
                st.markdown(f"**{i}.** [{eng} engagements]({post['url']})")
        
        with col2:
            st.markdown("#### By Impressions")
            for i, post in enumerate(data['top_by_impressions'][:5], 1):
                imp = post.get('impressions', 'N/A')
                st.markdown(f"**{i}.** [{imp:,} impressions]({post['url']})")

# Footer
st.markdown("""
<div class="footer">
    <div style="color: #667eea; font-weight: 600;">PostPro V2.0</div>
    <div style="color: #4a5568; margin-top: 5px;">Built by Nadav Druker • The Reputation Guardian</div>
</div>
""", unsafe_allow_html=True)
