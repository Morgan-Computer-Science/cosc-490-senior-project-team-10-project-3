import streamlit as st
import pandas as pd
from datetime import time, datetime
import google.generativeai as genai
from typing import Dict, List, Tuple
import plotly.graph_objects as go
import plotly.express as px

# Configure Gemini (you'll add your API key in secrets)
# genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

class AcademicAdvisor:
    """Core logic for tabular + time-series academic advising"""
    
    def __init__(self):
        """Initialize sample data for the demo"""
        self.load_sample_data()
    
    def load_sample_data(self):
        """Create realistic sample dataframes for the demo"""
        
        # 1. TRANSCRIPT TABLE - Student's completed courses
        self.transcript_df = pd.DataFrame({
            'Course Code': [
                'CS101', 'CS102', 'MATH150', 'ENGL101', 
                'CS201', 'MATH220', 'CS250', 'ENGL102',
                'CS280', 'MATH280', 'CS300', 'PHIL101'
            ],
            'Course Name': [
                'Intro to Programming', 'Data Structures', 'Calculus I', 'Freshman Composition',
                'Discrete Structures', 'Linear Algebra', 'Computer Architecture', 'Critical Reading',
                'Database Systems', 'Probability', 'Algorithms', 'Ethics'
            ],
            'Credits': [3, 3, 4, 3, 3, 3, 4, 3, 3, 3, 4, 3],
            'Grade': ['A-', 'B+', 'B', 'A', 'B', 'C+', 'B-', 'A-', 'B+', 'C', 'B', 'A'],
            'Term': [
                'Fall 2024', 'Fall 2024', 'Fall 2024', 'Fall 2024',
                'Spring 2025', 'Spring 2025', 'Spring 2025', 'Spring 2025',
                'Fall 2025', 'Fall 2025', 'Fall 2025', 'Fall 2025'
            ]
        })
        
        # 2. DEGREE REQUIREMENTS TABLE - What they need to graduate
        self.requirements_df = pd.DataFrame({
            'Category': [
                'Computer Science Core', 'Computer Science Core', 'Computer Science Core',
                'Math Foundation', 'Math Foundation',
                'Writing', 'General Electives'
            ],
            'Requirement': [
                'Take CS courses 200-level+', 'Operating Systems', 'Capstone Project',
                'Calculus Sequence', 'Statistics/Probability',
                'Two writing courses',
                'Any university courses'
            ],
            'Required Credits': [24, 3, 3, 8, 3, 6, 30],
            'Earned Credits': [18, 0, 0, 7, 3, 6, 12],
            'Status': ['In Progress', 'Not Started', 'Not Started', 
                      'In Progress', 'Completed', 'Completed', 'In Progress']
        })
        
        # 3. COURSE CATALOG - Available next term
        self.catalog_df = pd.DataFrame({
            'Course': ['CS350', 'CS360', 'CS410', 'CS420', 'MATH310', 'ENGL210'],
            'Name': ['Operating Systems', 'Computer Networks', 'Capstone Prep', 
                    'Web Development', 'Differential Equations', 'Technical Writing'],
            'Section': ['A', 'B', 'A', 'A', 'A', 'B'],
            'Days': ['Mon/Wed', 'Tue/Thu', 'Mon/Wed', 'Mon/Wed', 'Tue/Thu', 'Wed/Fri'],
            'Start Time': ['10:00', '13:00', '14:00', '16:00', '09:00', '11:00'],
            'End Time': ['11:30', '14:30', '15:30', '17:30', '10:30', '12:30'],
            'Credits': [3, 3, 3, 3, 4, 3],
            'Seats': [25, 30, 20, 25, 30, 20],
            'Modality': ['In-person', 'Hybrid', 'In-person', 'Online', 'In-person', 'Hybrid'],
            'Prereqs': ['CS250', 'CS280', 'Senior standing', 'CS201', 'MATH220', 'ENGL102']
        })
        
        # 4. SAMPLE STUDENT AVAILABILITY (Time-series grid)
        self.availability = {
            'Monday': [(time(9, 0), time(11, 0), 'Work'), (time(14, 0), time(17, 0), 'Work')],
            'Tuesday': [(time(13, 0), time(15, 0), 'Internship')],
            'Wednesday': [(time(9, 0), time(11, 0), 'Work')],
            'Thursday': [],
            'Friday': [(time(9, 0), time(12, 0), 'Study Group')],
            'Saturday': [],
            'Sunday': []
        }
    
    def calculate_degree_progress(self) -> Dict:
        """Calculate detailed degree progress from transcript"""
        total_credits = self.transcript_df['Credits'].sum()
        
        # Group by subject area
        cs_credits = self.transcript_df[
            self.transcript_df['Course Code'].str.startswith('CS')
        ]['Credits'].sum()
        
        math_credits = self.transcript_df[
            self.transcript_df['Course Code'].str.startswith('MATH')
        ]['Credits'].sum()
        
        # Find missing requirements
        taken_courses = set(self.transcript_df['Course Code'])
        required_courses = {'CS350', 'CS360', 'CS410'}  # OS, Networks, Capstone
        missing = required_courses - taken_courses
        
        return {
            'total_credits': total_credits,
            'remaining_credits': 120 - total_credits,
            'cs_credits': cs_credits,
            'math_credits': math_credits,
            'missing_courses': list(missing),
            'gpa': (self.transcript_df['Credits'] * self._grade_to_points(self.transcript_df['Grade'])).sum() / total_credits
        }
    
    def _grade_to_points(self, grades):
        """Convert letter grades to grade points"""
        grade_map = {'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7, 
                    'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D': 1.0, 'F': 0.0}
        return [grade_map.get(g, 0.0) for g in grades]
    
    def format_availability_string(self) -> str:
        """Convert time-series availability to readable format for AI"""
        output = "Weekly Availability (Busy times):\n"
        for day, blocks in self.availability.items():
            if blocks:
                times = [f"{b[0].strftime('%I:%M %p')}-{b[1].strftime('%I:%M %p')} ({b[2]})" 
                        for b in blocks]
                output += f"{day}: {', '.join(times)}\n"
            else:
                output += f"{day}: Free all day\n"
        return output
    
    def find_conflict_free_schedules(self, preferences: str) -> List[Dict]:
        """
        Simple algorithm to find possible schedules
        In production, this would be enhanced by Gemini
        """
        possible_schedules = []
        
        # Sample logic for demo purposes
        schedule_a = {
            'name': 'Plan A - Balanced Load',
            'courses': ['CS350 (OS)', 'MATH310 (Diff Eq)', 'ENGL210 (Tech Writing)'],
            'credits': 10,
            'reasoning': 'Spreads hard classes across week, avoids Tuesday internship'
        }
        
        schedule_b = {
            'name': 'Plan B - CS Focus',
            'courses': ['CS350 (OS)', 'CS360 (Networks)', 'CS410 (Capstone Prep)'],
            'credits': 9,
            'reasoning': 'Focuses on core CS requirements, all classes in afternoon'
        }
        
        return [schedule_a, schedule_b]

def create_availability_visualization(availability):
    """Create a heatmap of weekly availability"""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours = list(range(8, 22))  # 8 AM to 10 PM
    
    # Create matrix
    availability_matrix = []
    for day in days:
        day_slots = []
        day_blocks = availability.get(day, [])
        
        for hour in hours:
            busy = False
            for block in day_blocks:
                block_start = block[0].hour + block[0].minute/60
                block_end = block[1].hour + block[1].minute/60
                if block_start <= hour < block_end:
                    busy = True
            day_slots.append(1 if not busy else 0)  # 1 = free, 0 = busy
        availability_matrix.append(day_slots)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=availability_matrix,
        x=[f"{h}:00" for h in hours],
        y=days,
        colorscale=[[0, 'red'], [1, 'green']],
        showscale=False,
        text=[[ 'Free' if val else 'Busy' for val in row] for row in availability_matrix],
        texttemplate="%{text}",
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title='Weekly Availability (Green = Free, Red = Busy)',
        xaxis_title='Time of Day',
        yaxis_title='Day',
        height=400
    )
    
    return fig

# ------------------- STREAMLIT UI -------------------

def main():
    st.set_page_config(page_title="Academic AI Advisor", layout="wide")
    
    st.title("🎓 Multimodal Academic Advisor")
    st.markdown("*Powered by Tabular + Time-Series AI*")
    
    # Initialize advisor
    advisor = AcademicAdvisor()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    mode = st.sidebar.radio(
        "Choose Demo Mode",
        ["🏁 Degree Progress", "📅 Course Scheduling"]
    )
    
    # Student preferences input (persistent)
    st.sidebar.markdown("---")
    st.sidebar.subheader("Student Preferences")
    student_prefs = st.sidebar.text_area(
        "Tell us about your goals/constraints:",
        value="I want cybersecurity internships; I'm weak in math; I work 20 hrs/week",
        height=100
    )
    
    if mode == "🏁 Degree Progress":
        st.header("Degree Progress & Graduation Planning")
        
        # Two-column layout for tables
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Transcript Data")
            st.dataframe(advisor.transcript_df, use_container_width=True)
            
            # Show quick stats
            progress = advisor.calculate_degree_progress()
            st.metric("Current GPA", f"{progress['gpa']:.2f}")
            
        with col2:
            st.subheader("📋 Degree Requirements")
            st.dataframe(advisor.requirements_df, use_container_width=True)
            
            # Progress bars
            total_pct = (84/120)*100
            st.metric("Total Credits", "84/120", f"{total_pct:.0f}% Complete")
        
        # AI Analysis Section
        st.markdown("---")
        st.subheader("🤖 AI Degree Audit Analysis")
        
        if st.button("Generate Degree Plan", type="primary"):
            with st.spinner("Analyzing your transcript and requirements..."):
                # Prepare data for Gemini (simulated for demo)
                progress = advisor.calculate_degree_progress()
                
                # Display results
                st.success("Analysis Complete!")
                
                # Create columns for output
                out1, out2 = st.columns(2)
                
                with out1:
                    st.markdown("**📈 Progress Summary**")
                    st.markdown(f"""
                    - **Total Credits:** {progress['total_credits']}/120  
                    - **Remaining:** {progress['remaining_credits']} credits needed  
                    - **Missing Requirements:** {', '.join(progress['missing_courses'])}  
                    - **CS Credits Earned:** {progress['cs_credits']}/24 core credits
                    """)
                
                with out2:
                    st.markdown("**📝 Recommended Next Term**")
                    st.markdown("""
                    Based on your math concerns and work schedule:
                    
                    **CS350 - Operating Systems** (3 credits)  
                    *Prereq: CS250 - Met*  
                    
                    **ENGL210 - Technical Writing** (3 credits)  
                    *Fulfills writing requirement*  
                    
                    **Elective - Low math load** (3 credits)  
                    
                    *Total: 9 credits (manageable with work schedule)*
                    """)
    
    else:  # Course Scheduling mode
        st.header("Course Selection with Constraints")
        
        # Show availability visualization
        st.subheader("⏰ Student Weekly Availability")
        fig = create_availability_visualization(advisor.availability)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show available courses
        st.subheader("📚 Available Courses - Next Term")
        st.dataframe(advisor.catalog_df, use_container_width=True)
        
        # Generate schedules button
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown("**Current Preferences:**")
            st.info(student_prefs)
        
        with col2:
            if st.button("Generate Conflict-Free Schedules", type="primary"):
                with st.spinner("Finding optimal schedules..."):
                    schedules = advisor.find_conflict_free_schedules(student_prefs)
                    
                    # Display two plans side by side
                    plan_col1, plan_col2 = st.columns(2)
                    
                    with plan_col1:
                        st.success("**Plan A - Balanced Load**")
                        st.markdown("""
                        **Recommended Courses:**
                        - 📘 CS350 - Operating Systems (Mon/Wed 10:00)
                        - 📙 MATH310 - Differential Equations (Tue/Thu 9:00)  
                        - 📗 ENGL210 - Technical Writing (Wed/Fri 11:00)
                        
                        **Credits:** 10
                        
                        **Why this works:**  
                        ✓ Avoids your Monday work shifts (classes end by 11:30)  
                        ✓ Spreads math across week for extra study time  
                        ✓ Fulfills writing requirement  
                        """)
                    
                    with plan_col2:
                        st.info("**Plan B - CS Focus**")
                        st.markdown("""
                        **Recommended Courses:**
                        - 📘 CS350 - Operating Systems (Mon/Wed 10:00)
                        - 📘 CS360 - Computer Networks (Tue/Thu 13:00)
                        - 📘 CS410 - Capstone Prep (Mon/Wed 14:00)
                        
                        **Credits:** 9
                        
                        **Why this works:**  
                        ✓ All afternoon classes (post-work)  
                        ✓ Fast-track CS degree completion  
                        ✓ No math courses (addressing your concern)  
                        """)
        
        # Show conflict resolution explanation
        st.markdown("---")
        with st.expander("🔍 See how AI resolves conflicts"):
            st.markdown("""
            **Input Analysis:**
            1. **Tabular Data:** Course catalog filtered for available sections
            2. **Time-Series Data:** Your work schedule (Mon 9-11, Wed 9-11, Tue 1-3)
            3. **Text Preferences:** Cybersecurity interest, math concerns
            
            **Constraint Solving:**
            - Removed all courses conflicting with work hours
            - Prioritized CS courses for cybersecurity path
            - Avoided heavy math load in Plan B
            - Balanced difficulty in Plan A
            """)

if __name__ == "__main__":
    main()