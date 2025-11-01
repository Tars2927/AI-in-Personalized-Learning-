import streamlit as st
import pandas as pd
import joblib
import google.generativeai as genai
import os
import plotly.graph_objects as go
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AI Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Main background and text */
    .stApp {
        background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(120deg, #6366f1 0%, #8b5cf6 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e3f 0%, #2d2d4a 100%);
    }
    
    [data-testid="stSidebar"] h2 {
        color: #a5b4fc;
        font-size: 1.3rem;
        font-weight: 600;
        padding-bottom: 1rem;
        border-bottom: 2px solid #4f46e5;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #2d2d4a 0%, #3d3d5a 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #8b5cf6;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .metric-label {
        color: #a5b4fc;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 700;
        margin-top: 0.5rem;
    }
    
    /* Prediction result box */
    .prediction-box {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(79, 70, 229, 0.4);
    }
    
    .prediction-box h2 {
        color: white;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .prediction-box .grade {
        color: white;
        font-size: 3.5rem;
        font-weight: 800;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
    }
    
    /* Comparison box */
    .comparison-box {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
    }
    
    .comparison-box.negative {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
    }
    
    .comparison-box h3 {
        color: white;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    
    .comparison-box .diff {
        color: white;
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Response container */
    .response-container {
        background: rgba(45, 45, 74, 0.6);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid rgba(139, 92, 246, 0.3);
        margin-top: 2rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(45, 45, 74, 0.4);
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #a5b4fc;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(120deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(120deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        transition: all 0.3s ease;
        width: 100%;
        font-size: 1.1rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        background: #4f46e5;
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Quiz container */
    .quiz-container {
        background: rgba(45, 45, 74, 0.6);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid rgba(139, 92, 246, 0.3);
        margin-top: 1rem;
    }
    
    /* What-if section */
    .whatif-section {
        background: rgba(45, 45, 74, 0.4);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px dashed rgba(139, 92, 246, 0.5);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- API & MODEL CONFIGURATION ---
try:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    if not GEMINI_API_KEY:
        st.error("⚠️ GEMINI_API_KEY is not set. Please configure your API key.")
        st.stop()

    genai.configure(api_key=GEMINI_API_KEY)
    llm = genai.GenerativeModel('gemini-2.5-pro')
    model = joblib.load('student_model.pkl')

except Exception as e:
    st.error(f"❌ An error occurred during initialization: {e}")
    st.stop()

# --- CONSTANTS ---
MODEL_COLUMNS = ['age', 'Medu', 'Fedu', 'traveltime', 'studytime', 'failures',
                 'famrel', 'freetime', 'goout', 'Dalc', 'Walc', 'health', 'absences',
                 'G1', 'G2', 'school_MS', 'sex_M', 'address_U', 'famsize_LE3',
                 'Pstatus_T', 'Mjob_health', 'Mjob_other', 'Mjob_services',
                 'Mjob_teacher', 'Fjob_health', 'Fjob_other', 'Fjob_services',
                 'Fjob_teacher', 'reason_home', 'reason_other', 'reason_reputation',
                 'guardian_mother', 'guardian_other', 'schoolsup_yes', 'famsup_yes',
                 'paid_yes', 'activities_yes', 'nursery_yes', 'higher_yes',
                 'internet_yes', 'romantic_yes']

# --- HELPER FUNCTIONS ---
def predict_grade(studytime, failures, goout, absences):
    """Make a grade prediction based on input parameters"""
    input_df = pd.DataFrame(0, index=[0], columns=MODEL_COLUMNS)
    input_df['studytime'] = studytime
    input_df['failures'] = failures
    input_df['goout'] = goout
    input_df['absences'] = absences
    input_df['age'] = 17
    input_df['G1'] = 11
    input_df['G2'] = 11
    return model.predict(input_df)[0]

def create_sensitivity_chart(base_studytime, base_failures, base_goout, base_absences):
    """Create a bar chart showing impact of changing each variable"""
    base_grade = predict_grade(base_studytime, base_failures, base_goout, base_absences)
    
    # Calculate impact of improving each factor
    impacts = []
    
    # Study time impact (increase by 1)
    if base_studytime < 4:
        new_grade = predict_grade(base_studytime + 1, base_failures, base_goout, base_absences)
        impacts.append({
            'Factor': 'Study Time +1',
            'Impact': new_grade - base_grade,
            'Description': 'Increase weekly study time'
        })
    
    # Reduce failures (if any)
    if base_failures > 0:
        new_grade = predict_grade(base_studytime, base_failures - 1, base_goout, base_absences)
        impacts.append({
            'Factor': 'Fewer Failures',
            'Impact': new_grade - base_grade,
            'Description': 'Reduce past failures by 1'
        })
    
    # Reduce socializing (if high)
    if base_goout > 2:
        new_grade = predict_grade(base_studytime, base_failures, base_goout - 1, base_absences)
        impacts.append({
            'Factor': 'Less Socializing',
            'Impact': new_grade - base_grade,
            'Description': 'Reduce going out by 1 level'
        })
    
    # Reduce absences
    if base_absences > 5:
        new_grade = predict_grade(base_studytime, base_failures, base_goout, max(0, base_absences - 5))
        impacts.append({
            'Factor': 'Better Attendance',
            'Impact': new_grade - base_grade,
            'Description': 'Reduce absences by 5'
        })
    
    df = pd.DataFrame(impacts)
    
    if len(df) > 0:
        df = df.sort_values('Impact', ascending=True)
        
        fig = go.Figure()
        
        colors = ['#10b981' if x > 0 else '#ef4444' for x in df['Impact']]
        
        fig.add_trace(go.Bar(
            y=df['Factor'],
            x=df['Impact'],
            orientation='h',
            marker=dict(color=colors, line=dict(color='rgba(255,255,255,0.3)', width=1)),
            text=[f"+{x:.2f}" if x > 0 else f"{x:.2f}" for x in df['Impact']],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Grade Impact: %{x:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text='Impact of Habit Changes on Your Grade',
                font=dict(size=18, color='#ffffff', family='Arial, sans-serif'),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title='Grade Point Change',
                gridcolor='rgba(165, 180, 252, 0.2)',
                zerolinecolor='rgba(165, 180, 252, 0.4)',
                tickfont=dict(color='#a5b4fc')
            ),
            yaxis=dict(
                tickfont=dict(color='#ffffff', size=12)
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(30, 30, 63, 0.3)',
            font=dict(color='#ffffff'),
            height=300,
            margin=dict(l=20, r=80, t=60, b=40),
            showlegend=False
        )
        
        return fig, df
    else:
        return None, None

def create_radar_chart(studytime, failures, goout, absences):
    """Create a radar chart to visualize student habits"""
    study_score = (studytime / 4) * 100
    failure_score = 100 - ((failures / 4) * 100)
    social_score = (goout / 5) * 100
    attendance_score = max(0, 100 - (absences / 93) * 100)
    
    categories = ['Study Time', 'Academic Success', 'Social Balance', 'Attendance']
    values = [study_score, failure_score, social_score, attendance_score]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(139, 92, 246, 0.3)',
        line=dict(color='rgb(139, 92, 246)', width=3),
        marker=dict(size=8, color='rgb(139, 92, 246)'),
        name='Your Profile'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=True,
                ticks='',
                gridcolor='rgba(165, 180, 252, 0.3)',
                tickfont=dict(color='#a5b4fc', size=10)
            ),
            angularaxis=dict(
                gridcolor='rgba(165, 180, 252, 0.3)',
                linecolor='rgba(165, 180, 252, 0.3)',
                tickfont=dict(color='#ffffff', size=12, family='Arial, sans-serif')
            ),
            bgcolor='rgba(30, 30, 63, 0.5)'
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff'),
        height=400,
        margin=dict(l=80, r=80, t=40, b=40)
    )
    
    return fig

def create_master_prompt(student_data, predicted_grade, style):
    prompt = f"""
    You are an expert AI academic advisor. Your tone is supportive and encouraging.

    A student has provided the following information:
    - Weekly Study Time (1-4): {student_data['studytime']}
    - Past Class Failures: {student_data['failures']}
    - Socializing (1-5): {student_data['goout']}
    - Absences: {student_data['absences']}
    - Preferred Learning Style: {style}

    Our predictive model estimates their final grade will be {predicted_grade:.2f} out of 20.

    Your task is to provide two things in your response:

    1.  **Personalized Advice:** Write a short paragraph of feedback (3-4 sentences) tailored to the student's **{style}** learning style.
    2.  **Actionable Resource:** Recommend one specific, real, and free online resource (like a YouTube video, a website, or a free app) that aligns with their **{style}**.

    Structure your response with markdown headings for "Personalized Advice" and "Recommended Resource".
    """
    return prompt

def generate_quiz(topic, difficulty, num_questions):
    """Generate a custom quiz based on user input"""
    prompt = f"""
    Create a quiz on the topic: **{topic}**
    
    Requirements:
    - Difficulty level: {difficulty}
    - Number of questions: {num_questions}
    - Format: Multiple choice with 4 options (A, B, C, D)
    - Include the correct answer at the end of each question
    - Make questions engaging and educational
    
    Structure each question as follows:
    **Question X:**
    [Question text]
    
    A) [Option A]
    B) [Option B]
    C) [Option C]
    D) [Option D]
    
    **Correct Answer:** [Letter]
    **Explanation:** [Brief explanation why this is correct]
    
    ---
    
    Start generating the quiz now!
    """
    return prompt

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>🎓 AI Personalized Learning Assistant</h1>
    <p>Harness the power of AI to predict your academic performance and receive tailored learning recommendations</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 📊 Student Profile")
    st.markdown("---")
    
    st.markdown("### 📚 Academic Habits")
    studytime = st.slider('Weekly Study Time', 1, 4, 2, 
                          help="1 = <2 hours, 2 = 2-5 hours, 3 = 5-10 hours, 4 = >10 hours")
    failures = st.slider('Past Class Failures', 0, 4, 0,
                        help="Number of previous academic failures")
    absences = st.slider('School Absences', 0, 93, 5,
                        help="Total number of absences this term")
    
    st.markdown("### 👥 Social Life")
    goout = st.slider('Socializing Frequency', 1, 5, 3,
                     help="1 = Very low, 5 = Very high")
    
    st.markdown("### 🧠 Learning Preference")
    learning_style = st.selectbox(
        "Preferred Learning Style",
        ("Visual", "Auditory", "Reading/Writing", "Kinesthetic"),
        help="Choose the learning style that works best for you"
    )
    
    st.markdown("---")
    st.markdown('<div class="info-box">💡 Tip: Be honest with your inputs for the most accurate predictions!</div>', 
                unsafe_allow_html=True)

# --- MAIN CONTENT WITH TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📈 Grade Prediction", "🔮 What-If Analysis", "🎯 Profile Visualization", "📝 Quiz Generator"])

# TAB 1: GRADE PREDICTION
with tab1:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Study Time</div>
            <div class="metric-value">{studytime}/4</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Failures</div>
            <div class="metric-value">{failures}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Social Level</div>
            <div class="metric-value">{goout}/5</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Absences</div>
            <div class="metric-value">{absences}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Generate My Personalized Plan", key="predict_btn"):
        predicted_grade = predict_grade(studytime, failures, goout, absences)
        
        st.markdown(f"""
        <div class="prediction-box">
            <h2>🎯 Predicted Final Grade</h2>
            <div class="grade">{predicted_grade:.2f} / 20</div>
        </div>
        """, unsafe_allow_html=True)

        input_df = pd.DataFrame(0, index=[0], columns=MODEL_COLUMNS)
        input_df['studytime'] = studytime
        input_df['failures'] = failures
        input_df['goout'] = goout
        input_df['absences'] = absences

        with st.spinner("✨ Crafting your personalized learning plan..."):
            master_prompt = create_master_prompt(input_df.iloc[0], predicted_grade, learning_style)
            response = llm.generate_content(master_prompt)
            
            st.markdown('<div class="response-container">', unsafe_allow_html=True)
            st.markdown("## 📝 Your Personalized Learning Plan")
            st.markdown(response.text)
            st.markdown('</div>', unsafe_allow_html=True)

# TAB 2: WHAT-IF ANALYSIS
with tab2:
    st.markdown("## 🔮 What-If Analysis: Explore Your Potential")
    st.markdown("See how different habit changes could impact your final grade. Experiment with different scenarios!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Current prediction
    current_grade = predict_grade(studytime, failures, goout, absences)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="prediction-box">
            <h2>📊 Current Prediction</h2>
            <div class="grade">{current_grade:.2f} / 20</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Sensitivity analysis
    st.markdown("### 📈 Impact of Improving Your Habits")
    sensitivity_fig, sensitivity_df = create_sensitivity_chart(studytime, failures, goout, absences)
    
    if sensitivity_fig:
        st.plotly_chart(sensitivity_fig, use_container_width=True)
        
        st.markdown('<div class="response-container">', unsafe_allow_html=True)
        st.markdown("#### 💡 Key Insights")
        
        if len(sensitivity_df) > 0:
            best_improvement = sensitivity_df.iloc[-1]
            st.markdown(f"""
            <p style='color: #e0e7ff; font-size: 1.1rem;'>
            <strong>Best opportunity for improvement:</strong> {best_improvement['Description']} 
            could increase your grade by <strong style='color: #10b981;'>+{best_improvement['Impact']:.2f} points</strong>!
            </p>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("🎉 You're already at optimal levels! Keep up the great work!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Interactive What-If Simulator
    st.markdown("### 🎮 Interactive Scenario Simulator")
    st.markdown('<div class="whatif-section">', unsafe_allow_html=True)
    st.markdown("**Adjust the sliders below to test different scenarios:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        whatif_studytime = st.slider('What if my study time was...', 1, 4, studytime, key='whatif_study')
        whatif_failures = st.slider('What if I had... failures', 0, 4, failures, key='whatif_fail')
    
    with col2:
        whatif_goout = st.slider('What if I went out... often', 1, 5, goout, key='whatif_goout')
        whatif_absences = st.slider('What if I had... absences', 0, 93, absences, key='whatif_abs')
    
    whatif_grade = predict_grade(whatif_studytime, whatif_failures, whatif_goout, whatif_absences)
    grade_diff = whatif_grade - current_grade
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        diff_class = "" if grade_diff >= 0 else "negative"
        sign = "+" if grade_diff >= 0 else ""
        emoji = "📈" if grade_diff > 0 else "📉" if grade_diff < 0 else "➡️"
        
        st.markdown(f"""
        <div class="comparison-box {diff_class}">
            <h3>{emoji} Scenario Result</h3>
            <div class="grade">{whatif_grade:.2f} / 20</div>
            <div class="diff">{sign}{grade_diff:.2f} points</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Comparison table
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Detailed Comparison")
    
    comparison_data = {
        'Metric': ['Study Time', 'Past Failures', 'Going Out', 'Absences', '**Predicted Grade**'],
        'Current': [studytime, failures, goout, absences, f"**{current_grade:.2f}**"],
        'Scenario': [whatif_studytime, whatif_failures, whatif_goout, whatif_absences, f"**{whatif_grade:.2f}**"],
        'Change': [
            f"{whatif_studytime - studytime:+d}",
            f"{whatif_failures - failures:+d}",
            f"{whatif_goout - goout:+d}",
            f"{whatif_absences - absences:+d}",
            f"**{grade_diff:+.2f}**"
        ]
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

# TAB 3: STUDENT PROFILE VISUALIZATION
with tab3:
    st.markdown("## 🎯 Your Student Habits Radar")
    st.markdown("This visualization shows your strengths and areas for improvement across key academic dimensions.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    radar_fig = create_radar_chart(studytime, failures, goout, absences)
    st.plotly_chart(radar_fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="response-container">
            <h3>📊 How to Read Your Profile</h3>
            <p style='color: #e0e7ff;'>
            <strong>Study Time:</strong> Higher is better - shows dedication to learning<br>
            <strong>Academic Success:</strong> Based on past performance (fewer failures = higher score)<br>
            <strong>Social Balance:</strong> Moderate levels are healthy for well-being<br>
            <strong>Attendance:</strong> Higher scores indicate better attendance habits
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="response-container">
            <h3>💡 Quick Insights</h3>
            <p style='color: #e0e7ff;'>
            A balanced profile typically shows scores between 60-80 across all dimensions. 
            Extremely high or low values in any area may indicate opportunities for adjustment 
            to optimize your academic success and personal well-being.
            </p>
        </div>
        """, unsafe_allow_html=True)

# TAB 4: QUIZ GENERATOR
with tab4:
    st.markdown("## 📝 Dynamic Quiz Generator")
    st.markdown("Generate custom quizzes on any topic to test your knowledge!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        quiz_topic = st.text_input(
            "🎯 Enter a topic",
            placeholder="e.g., Python Programming, World History, Biology...",
            help="Type any subject you want to be quizzed on"
        )
    
    with col2:
        num_questions = st.selectbox(
            "Number of Questions",
            [3, 5, 10, 15],
            index=1
        )
    
    difficulty = st.select_slider(
        "Difficulty Level",
        options=["Beginner", "Intermediate", "Advanced"],
        value="Intermediate"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🎲 Generate Quiz", key="quiz_btn"):
        if quiz_topic.strip():
            with st.spinner(f"✨ Generating your {difficulty.lower()} quiz on {quiz_topic}..."):
                quiz_prompt = generate_quiz(quiz_topic, difficulty, num_questions)
                quiz_response = llm.generate_content(quiz_prompt)
                
                st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
                st.markdown(f"### 📚 Quiz: {quiz_topic}")
                st.markdown(f"**Difficulty:** {difficulty} | **Questions:** {num_questions}")
                st.markdown("---")
                st.markdown(quiz_response.text)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Please enter a topic for your quiz!")

# --- FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #a5b4fc; font-size: 0.9rem;'>Made by TARS • Built with ❤️ for Student Success</p>",
    unsafe_allow_html=True
)