import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Configure page
st.set_page_config(
    page_title="AI-Powered Polymer Composite Properties Predictor",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.sub-header {
    font-size: 1.5rem;
    color: #ff7f0e;
    margin-bottom: 1rem;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem;
    text-align: center;
}
.info-box {
    background-color: #e7f3ff;
    padding: 1rem;
    border-radius: 10px;
    border-left: 5px solid #1f77b4;
    margin: 1rem 0;
}
.logo-container {
    position: fixed;
    top: 10px;
    left: 10px;
    z-index: 999;
    background-color: white;
    padding: 5px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

def add_logo():
    """Add company logo to the top-left corner"""
    col1, col2, col3 = st.columns([1, 6, 1])
    
    with col1:
        try:
            st.image("Drisa_Logo.png", width=150)
        except:
            st.markdown("**Your Company Logo**")
    
    with col2:
        st.empty()
    
    with col3:
        st.empty()

class PolymerCompositeApp:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoders = {}
        self.feature_names = None
        self.target_names = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model and preprocessors"""
        try:
            model_data = joblib.load('polymer_composite_model.pkl')
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoders = model_data['label_encoders']
            self.feature_names = model_data['feature_names']
            self.target_names = model_data['target_names']
            return True
        except FileNotFoundError:
            st.error("Model file not found. Please train the model first.")
            return False
        except Exception as e:
            st.error(f"Error loading model: {str(e)}")
            return False
    
    def predict(self, input_data):
        """Make predictions on input data"""
        if self.model is None:
            return None
        
        try:
            # Scale the input data
            input_scaled = self.scaler.transform(input_data)
            
            # Make prediction
            predictions = self.model.predict(input_scaled)
            
            # Convert back to DataFrame
            predictions_df = pd.DataFrame(predictions, columns=self.target_names)
            
            # Convert electrical resistivity back from log scale
            predictions_df['Electrical_Resistivity_Ohm_m'] = 10 ** predictions_df['Electrical_Resistivity_Ohm_m']
            
            return predictions_df
        except Exception as e:
            st.error(f"Error making prediction: {str(e)}")
            return None
    
    def get_feature_importance(self):
        """Get feature importance for visualization"""
        if self.model is None:
            return None
        
        importance_dict = {}
        for i, target in enumerate(self.target_names):
            importance_dict[target] = dict(zip(
                self.feature_names, 
                self.model.estimators_[i].feature_importances_
            ))
        
        return importance_dict

def main():
    # Add company logo at the top
    add_logo()
    
    # Initialize app
    app = PolymerCompositeApp()
    
    # Main header
    st.markdown('<h1 class="main-header">🧪 AI-Powered Polymer Composite Properties Predictor</h1>', unsafe_allow_html=True)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Predictor", "About", "Model Performance", "Dataset Info"])
    
    if page == "Predictor":
        predictor_page(app)
    elif page == "About":
        about_page()
    elif page == "Model Performance":
        model_performance_page(app)
    elif page == "Dataset Info":
        dataset_info_page()

def predictor_page(app):
    """Main prediction page"""
    st.markdown('<h2 class="sub-header">Material Properties Prediction</h2>', unsafe_allow_html=True)
    
    # Create two columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Input Parameters")
        
        # Material selection
        polymer_matrices = ['Epoxy', 'Polyester', 'Vinyl Ester', 'Phenolic', 'Polyurethane']
        filler_types = ['Bovine Bone Particles', 'Hydroxyapatite', 'Bamboo Fibers', 
                       'Wood Flour', 'Rice Husk', 'Coconut Coir', 'Jute Fibers',
                       'Flax Fibers', 'Hemp Fibers', 'Chitosan Particles']
        
        polymer_matrix = st.selectbox("Polymer Matrix", polymer_matrices)
        filler_type = st.selectbox("Filler Type", filler_types)
        
        # Composition parameters
        filler_ratio = st.slider("Filler Ratio (wt%)", 0.0, 50.0, 25.0, 0.1)
        matrix_ratio = 100.0 - filler_ratio
        
        st.write(f"Matrix Ratio: {matrix_ratio:.1f} wt%")
        
        # Processing parameters
        curing_temp = st.slider("Curing Temperature (°C)", 60.0, 180.0, 120.0, 1.0)
        curing_time = st.slider("Curing Time (hours)", 2.0, 24.0, 8.0, 0.5)
        pressure = st.slider("Pressure (MPa)", 0.1, 10.0, 2.0, 0.1)
        particle_size = st.slider("Particle Size (μm)", 10.0, 500.0, 100.0, 1.0)
        density = st.slider("Density (g/cm³)", 1.0, 2.5, 1.5, 0.01)
        
        # Create input DataFrame
        input_data = pd.DataFrame({
            'Polymer_Matrix': [polymer_matrix],
            'Filler_Type': [filler_type],
            'Filler_Ratio_wt%': [filler_ratio],
            'Matrix_Ratio_wt%': [matrix_ratio],
            'Curing_Temperature_C': [curing_temp],
            'Curing_Time_hours': [curing_time],
            'Pressure_MPa': [pressure],
            'Particle_Size_microns': [particle_size],
            'Density_g_cm3': [density]
        })
        
        # Encode categorical variables
        for feature in ['Polymer_Matrix', 'Filler_Type']:
            if feature in app.label_encoders:
                input_data[feature] = app.label_encoders[feature].transform(input_data[feature])
        
        # Predict button
        if st.button("🔬 Predict Properties", type="primary"):
            with st.spinner("Predicting properties..."):
                predictions = app.predict(input_data)
                
                if predictions is not None:
                    st.session_state.predictions = predictions
                    st.success("Prediction completed!")
    
    with col2:
        st.markdown("### Predicted Properties")
        
        if 'predictions' in st.session_state:
            pred = st.session_state.predictions.iloc[0]
            
            # Create tabs for different property categories
            mech_tab, therm_tab, elec_tab = st.tabs(["Mechanical", "Thermal", "Electrical"])
            
            with mech_tab:
                st.markdown("#### Mechanical Properties")
                
                # Mechanical properties metrics
                col_mech1, col_mech2, col_mech3 = st.columns(3)
                
                with col_mech1:
                    st.metric("Tensile Strength", f"{pred['Tensile_Strength_MPa']:.2f} MPa")
                
                with col_mech2:
                    st.metric("Flexural Strength", f"{pred['Flexural_Strength_MPa']:.2f} MPa")
                
                with col_mech3:
                    st.metric("Impact Strength", f"{pred['Impact_Strength_J_m']:.2f} J/m")
                
                # Create gauge charts for mechanical properties
                fig_mech = make_subplots(
                    rows=1, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=["Tensile Strength", "Flexural Strength", "Impact Strength"]
                )
                
                fig_mech.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=pred['Tensile_Strength_MPa'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={'axis': {'range': [None, 200]},
                           'bar': {'color': "#1f77b4"},
                           'steps': [{'range': [0, 50], 'color': "lightgray"},
                                   {'range': [50, 100], 'color': "gray"}],
                           'threshold': {'line': {'color': "red", 'width': 4},
                                       'thickness': 0.75, 'value': 150}}
                ), row=1, col=1)
                
                fig_mech.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=pred['Flexural_Strength_MPa'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={'axis': {'range': [None, 250]},
                           'bar': {'color': "#ff7f0e"},
                           'steps': [{'range': [0, 75], 'color': "lightgray"},
                                   {'range': [75, 150], 'color': "gray"}],
                           'threshold': {'line': {'color': "red", 'width': 4},
                                       'thickness': 0.75, 'value': 200}}
                ), row=1, col=2)
                
                fig_mech.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=pred['Impact_Strength_J_m'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={'axis': {'range': [None, 50]},
                           'bar': {'color': "#2ca02c"},
                           'steps': [{'range': [0, 15], 'color': "lightgray"},
                                   {'range': [15, 30], 'color': "gray"}],
                           'threshold': {'line': {'color': "red", 'width': 4},
                                       'thickness': 0.75, 'value': 40}}
                ), row=1, col=3)
                
                fig_mech.update_layout(height=300)
                st.plotly_chart(fig_mech, use_container_width=True)
            
            with therm_tab:
                st.markdown("#### Thermal Properties")
                
                col_therm1, col_therm2, col_therm3 = st.columns(3)
                
                with col_therm1:
                    st.metric("Thermal Conductivity", f"{pred['Thermal_Conductivity_W_mK']:.3f} W/m·K")
                
                with col_therm2:
                    st.metric("Glass Transition Temp", f"{pred['Glass_Transition_Temp_C']:.1f} °C")
                
                with col_therm3:
                    st.metric("Thermal Expansion", f"{pred['Thermal_Expansion_ppm_C']:.1f} ppm/°C")
                
                # Bar chart for thermal properties
                thermal_data = {
                    'Property': ['Thermal Conductivity', 'Glass Transition Temp', 'Thermal Expansion'],
                    'Value': [pred['Thermal_Conductivity_W_mK'], pred['Glass_Transition_Temp_C'], pred['Thermal_Expansion_ppm_C']],
                    'Unit': ['W/m·K', '°C', 'ppm/°C']
                }
                
                fig_therm = go.Figure(data=[
                    go.Bar(x=thermal_data['Property'], y=thermal_data['Value'], 
                           marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'])
                ])
                fig_therm.update_layout(title="Thermal Properties", yaxis_title="Value")
                st.plotly_chart(fig_therm, use_container_width=True)
            
            with elec_tab:
                st.markdown("#### Electrical Properties")
                
                col_elec1, col_elec2 = st.columns(2)
                
                with col_elec1:
                    st.metric("Electrical Resistivity", f"{pred['Electrical_Resistivity_Ohm_m']:.2e} Ω·m")
                    st.metric("Dielectric Constant", f"{pred['Dielectric_Constant']:.2f}")
                
                with col_elec2:
                    st.metric("Dielectric Strength", f"{pred['Dielectric_Strength_kV_mm']:.2f} kV/mm")
                
                # Electrical properties visualization
                fig_elec = make_subplots(
                    rows=2, cols=2,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}],
                           [{"colspan": 2}, None]],
                    subplot_titles=["Dielectric Constant", "Dielectric Strength", "Electrical Resistivity"]
                )
                
                fig_elec.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=pred['Dielectric_Constant'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={'axis': {'range': [None, 10]},
                           'bar': {'color': "#d62728"},
                           'steps': [{'range': [0, 4], 'color': "lightgray"},
                                   {'range': [4, 6], 'color': "gray"}],
                           'threshold': {'line': {'color': "red", 'width': 4},
                                       'thickness': 0.75, 'value': 8}}
                ), row=1, col=1)
                
                fig_elec.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=pred['Dielectric_Strength_kV_mm'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={'axis': {'range': [None, 60]},
                           'bar': {'color': "#9467bd"},
                           'steps': [{'range': [0, 20], 'color': "lightgray"},
                                   {'range': [20, 40], 'color': "gray"}],
                           'threshold': {'line': {'color': "red", 'width': 4},
                                       'thickness': 0.75, 'value': 50}}
                ), row=1, col=2)
                
                # Log scale bar for electrical resistivity
                fig_elec.add_trace(go.Bar(
                    x=['Electrical Resistivity'],
                    y=[np.log10(pred['Electrical_Resistivity_Ohm_m'])],
                    marker_color='#8c564b',
                    name='log10(Resistivity)'
                ), row=2, col=1)
                
                fig_elec.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig_elec, use_container_width=True)
            
            # Summary table
            st.markdown("### Complete Results Summary")
            
            results_df = pd.DataFrame({
                'Property': [
                    'Tensile Strength', 'Flexural Strength', 'Impact Strength',
                    'Thermal Conductivity', 'Glass Transition Temperature', 'Thermal Expansion',
                    'Electrical Resistivity', 'Dielectric Constant', 'Dielectric Strength'
                ],
                'Value': [
                    f"{pred['Tensile_Strength_MPa']:.2f}",
                    f"{pred['Flexural_Strength_MPa']:.2f}",
                    f"{pred['Impact_Strength_J_m']:.2f}",
                    f"{pred['Thermal_Conductivity_W_mK']:.3f}",
                    f"{pred['Glass_Transition_Temp_C']:.1f}",
                    f"{pred['Thermal_Expansion_ppm_C']:.1f}",
                    f"{pred['Electrical_Resistivity_Ohm_m']:.2e}",
                    f"{pred['Dielectric_Constant']:.2f}",
                    f"{pred['Dielectric_Strength_kV_mm']:.2f}"
                ],
                'Unit': [
                    'MPa', 'MPa', 'J/m', 'W/m·K', '°C', 'ppm/°C', 'Ω·m', '-', 'kV/mm'
                ]
            })
            
            st.dataframe(results_df, use_container_width=True)
            
            # Download results
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name="polymer_composite_prediction.csv",
                mime="text/csv"
            )
        else:
            st.info("👆 Please input parameters and click 'Predict Properties' to see results.")

def about_page():
    """About page with project information"""
    st.markdown('<h2 class="sub-header">About This Application</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <h3>🎯 Project Overview</h3>
    <p>This AI-powered application predicts the mechanical, thermal, and electrical properties of polymer composite materials reinforced with natural biogenic fillers. The system uses machine learning to provide accurate property predictions based on material composition and processing parameters.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🧪 Supported Materials
        
        **Polymer Matrices:**
        - Epoxy
        - Polyester
        - Vinyl Ester
        - Phenolic
        - Polyurethane
        
        **Natural Biogenic Fillers:**
        - Bovine Bone Particles
        - Hydroxyapatite
        - Bamboo Fibers
        - Wood Flour
        - Rice Husk
        - Coconut Coir
        - Jute Fibers
        - Flax Fibers
        - Hemp Fibers
        - Chitosan Particles
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Predicted Properties
        
        **Mechanical Properties:**
        - Tensile Strength (MPa)
        - Flexural Strength (MPa)
        - Impact Strength (J/m)
        
        **Thermal Properties:**
        - Thermal Conductivity (W/m·K)
        - Glass Transition Temperature (°C)
        - Thermal Expansion (ppm/°C)
        
        **Electrical Properties:**
        - Electrical Resistivity (Ω·m)
        - Dielectric Constant
        - Dielectric Strength (kV/mm)
        """)
    
    st.markdown("""
    ### 🤖 Machine Learning Model
    
    The application uses a **Multi-Output Random Forest Regressor** trained on a synthetic dataset of 500 samples. The model:
    
    - Handles multiple input features including material composition, processing parameters, and physical properties
    - Simultaneously predicts 9 different material properties
    - Uses feature scaling and categorical encoding for optimal performance
    - Achieves high accuracy across all property predictions
    
    ### 📈 Key Features
    
    - **Real-time Predictions**: Get instant property predictions for your composite formulations
    - **Interactive Visualization**: Gauge charts and plots for easy interpretation
    - **Comprehensive Analysis**: Mechanical, thermal, and electrical property predictions
    - **Export Capabilities**: Download results in CSV format
    - **User-Friendly Interface**: Intuitive parameter input with sliders and dropdowns
    """)

def model_performance_page(app):
    """Model performance and feature importance page"""
    st.markdown('<h2 class="sub-header">Model Performance Analysis</h2>', unsafe_allow_html=True)
    
    # Feature importance
    importance_data = app.get_feature_importance()
    
    if importance_data:
        st.markdown("### 📊 Feature Importance Analysis")
        
        # Select property for feature importance display
        selected_property = st.selectbox(
            "Select property to view feature importance:",
            list(importance_data.keys())
        )
        
        # Create feature importance plot
        features = list(importance_data[selected_property].keys())
        importances = list(importance_data[selected_property].values())
        
        # Sort by importance
        sorted_data = sorted(zip(features, importances), key=lambda x: x[1], reverse=True)
        sorted_features, sorted_importances = zip(*sorted_data)
        
        fig = go.Figure(data=[
            go.Bar(
                y=sorted_features,
                x=sorted_importances,
                orientation='h',
                marker_color='#1f77b4'
            )
        ])
        
        fig.update_layout(
            title=f"Feature Importance for {selected_property}",
            xaxis_title="Importance",
            yaxis_title="Features",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Feature importance table
        importance_df = pd.DataFrame({
            'Feature': sorted_features,
            'Importance': sorted_importances
        })
        
        st.dataframe(importance_df, use_container_width=True)
    
    # Model information
    st.markdown("### 🔧 Model Details")
    
    model_info = {
        'Model Type': 'Multi-Output Random Forest Regressor',
        'Number of Estimators': '100',
        'Max Depth': '15',
        'Min Samples Split': '5',
        'Min Samples Leaf': '2',
        'Training Dataset Size': '500 samples',
        'Number of Features': '9',
        'Number of Target Properties': '9'
    }
    
    info_df = pd.DataFrame(list(model_info.items()), columns=['Parameter', 'Value'])
    st.dataframe(info_df, use_container_width=True)

def dataset_info_page():
    """Dataset information page"""
    st.markdown('<h2 class="sub-header">Dataset Information</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 📋 Dataset Overview
    
    The synthetic dataset was generated to simulate realistic polymer composite materials with natural biogenic fillers. 
    The dataset contains 500 samples with carefully designed relationships between input parameters and output properties.
    
    ### 🔬 Data Generation Methodology
    
    1. **Material Selection**: Random selection from supported polymer matrices and biogenic fillers
    2. **Composition Parameters**: Realistic mixing ratios (0-50% filler content)
    3. **Processing Parameters**: Industry-standard curing conditions
    4. **Property Calculation**: Physics-based relationships with realistic noise
    5. **Validation**: Ensuring all values are within realistic ranges
    
    ### 📊 Dataset Statistics
    """)
    
    # Dataset statistics
    stats_data = {
        'Parameter': [
            'Total Samples', 'Polymer Matrix Types', 'Filler Types', 'Input Features', 
            'Output Properties', 'Filler Ratio Range', 'Temperature Range', 'Pressure Range'
        ],
        'Value': [
            '500', '5', '10', '9', '9', '0-50 wt%', '60-180 °C', '0.1-10 MPa'
        ]
    }
    
    stats_df = pd.DataFrame(stats_data)
    st.dataframe(stats_df, use_container_width=True)
    
    st.markdown("""
    ### 🎯 Quality Assurance
    
    - **Realistic Relationships**: Based on known material science principles
    - **Noise Addition**: 10% realistic noise to simulate experimental variation
    - **Range Validation**: All properties within physically meaningful ranges
    - **Balanced Distribution**: Even representation of all material types
    - **Correlation Analysis**: Verified meaningful correlations between inputs and outputs
    """)

if __name__ == "__main__":
    main()
