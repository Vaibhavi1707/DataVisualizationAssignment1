import streamlit as st
import animate as anim

INPUT_MAP = {
    'Sea Surface Salinity': 'sss',
    'Sea Surface Temperature': 'sst',
    'Sea Surface Height Anomaly': 'ssha'
}
VIZ_TYPE_MAP = {
    'Scalar Field': 'scalar',
    'Vector Field': 'vector'
}

st.title('Indian Ocean Visualization')

viz_type = 'scalar'
with st.sidebar:
    st.header('Visualization Type')
    viz_type = st.selectbox('', ['Scalar Field', 'Vector Field'])

if VIZ_TYPE_MAP[viz_type] == 'scalar':
    st.subheader('Scalar Field Visualization')
    param = st.radio("", ("Sea Surface Salinity", "Sea Surface Temperature", "Sea Surface Height Anomaly"))
    anim.make_scalar_animation(INPUT_MAP[param])

elif VIZ_TYPE_MAP[viz_type] == 'vector':
    st.subheader('Vector Field Visualization')
    param = st.radio("", ("quiver plot", "magnitude contours", "both combined"))
    anim.make_vector_animation('../data/zonal-current/', param.split(' ')[0])
