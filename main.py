import streamlit as st
import networkx as nx
import pandas as pd
from graph_utils import *
from colorlist import *
import io
from zipfile import ZipFile



# Define color list for sectors with exact matching names

def get_unique_domains(df, col1, col2):
    unique_domains = set(df[col1].dropna().astype(str).str.strip()) | set(df[col2].dropna().astype(str).str.strip())

    return sorted(unique_domains)


def load_data(network_file):
    try:
        # Load node and edge data from uploaded Excel files
        df_nom = pd.read_excel(network_file, sheet_name="info élèves", usecols=["Caractéristiques des liens", "Dom_mi année 1", "Dom_mi année 2", "Domaine parcoursup", "PCS_Ménage", "Etablissement Parcoursup","Hors/dans Parcoursup"])
        df_network_lienplus = pd.read_excel(network_file, sheet_name="Liens +")
        df_network_lienmoins = pd.read_excel(network_file, sheet_name="Liens -")
        df_network_cantine = pd.read_excel(network_file, sheet_name="Cantine")
        df_network_orientation = pd.read_excel(network_file, sheet_name="Parler orientation")

        df_network_fin_annee = pd.read_excel(network_file, sheet_name="Fin d'année")
        df_network_etudes = pd.read_excel(network_file, sheet_name="Etudes sup (voir)")
        # st.dataframe(df_nom)
        # st.dataframe(df_network_cantine)
        # st.dataframe(df_network_lienplus)
        # st.dataframe(df_network_fin_annee)
        # st.dataframe(df_network_etudes)

        return df_nom, df_network_lienplus, df_network_lienmoins, df_network_cantine, df_network_orientation, df_network_fin_annee, df_network_etudes
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None, None

def create_node_data_domaine(df_nom, col1, col2=None):
    node_data = {}
    for _, row in df_nom.iterrows():
        domaines = []
        if pd.notna(row[col1]):
            domaines.append(row[col1])
        if col2 and pd.notna(row[col2]):
            domaines.append(row[col2])

        if domaines:  # Only add nodes with at least one domaine
            node_data[row["Caractéristiques des liens"]] = domaines
    return node_data

def create_node_data_type(df_nom, col1, col2=None):
    node_data = {}
    for _, row in df_nom.iterrows():
        types = []
        if pd.notna(row[col1]):
            types.append(row[col1])
        if col2 and pd.notna(row[col2]):
            types.append(row[col2])

        if types:  # Only add nodes with at least one domaine
            node_data[row["Caractéristiques des liens"]] = types
    return node_data

def create_node_data_simple(df_nom, col1):
    node_data = {row[col1]: [] for _, row in df_nom.iterrows() if pd.notna(row[col1])}

    return node_data

def create_edge_data(df_network):
    edge_data = []
    for _, row in df_network.iterrows():
        person1 = row.iloc[0]
        person2 = row.iloc[1]
        edge_data.append((person2, person1))
    return edge_data

def creat_edge_color(df_network):
    edge_color = []
    for _, row in df_network.iterrows():
        weight = 5 - row.iloc[2]
        match(weight):
            case 4:
                color = "mediumorchid"
            case 3 :
                color = "dodgerblue"
            case 2:
                color = "mediumaquamarine"
            case 1:
                color = "red"
            case 0:
                color = "indianred"
        edge_color.append(color)
    return edge_color

def create_edge_weight(df_network):
    edge_weight = []
    for _, row in df_network.iterrows():
        weight = 5 - row.iloc[2]
        edge_weight.append(weight)
    return edge_weight

def download_graphs(graphs):
    """
    Permet de télécharger tous les graphes en tant qu'images dans un fichier ZIP.
    
    Args:
        graphs (dict): Un dictionnaire contenant les noms des graphes comme clés et les objets matplotlib comme valeurs.
    """
    # Crée un fichier ZIP en mémoire
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "w") as zip_file:
        for graph_name, fig in graphs.items():
            # Sauvegarde chaque graphe dans un fichier PNG en mémoire
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format="png", bbox_inches="tight")
            img_buffer.seek(0)
            # Ajoute l'image au fichier ZIP
            zip_file.writestr(f"{graph_name}.png", img_buffer.read())
    
    zip_buffer.seek(0)
    
    # Ajoute un bouton de téléchargement dans Streamlit
    st.download_button(
        label="Télécharger tous les graphes (ZIP)",
        data=zip_buffer,
        file_name="graphs.zip",
        mime="application/zip"
    )

def main():
    st.set_page_config(page_title="Student Relation Map",layout="wide")
    st.title("Student Relation Map")
    st.write("Visualization of students relations using directed network graph")

    # File uploaders
    st.sidebar.header("Upload Data Files")
    network_file = st.sidebar.file_uploader("Upload Nodes Excel File (reseauv2.xlsx)", type=['xlsx'])

    if network_file is not None:
        df_nom, df_network_lienplus, df_network_lienmoins, df_network_cantine, df_network_orientation, df_network_fin_annee, df_network_etudes = load_data(network_file)
        if df_nom is None or df_network_lienplus is None or df_network_lienmoins is None or df_network_cantine is None or df_network_orientation is None or df_network_fin_annee is None or df_network_etudes is None:
            return
    else:
        st.info("Please upload a valid Excel file")
        return
    
    # unique_domains=get_unique_domains(df_nom, "Dom_mi année 1", "Dom_mi année 2")
    # st.write(unique_domains)

    graphs = {}

    # Create node data for the first graph
    node_data_simple = create_node_data_simple(df_nom, "Caractéristiques des liens")
    
    # Graphe des amitiés simple avec les amitiés de milieu d’année 
    edge_data_lienplus = create_edge_data(df_network_lienplus)
    edge_color_lienplus = creat_edge_color(df_network_lienplus)
    edge_weight_lienplus = create_edge_weight(df_network_lienplus)

    st.header("Liens d'amitié")
    fig1, pos = create_directed_graph("simple", node_data_simple, edge_data_lienplus, edge_color_lienplus, edge_width=1)
    st.pyplot(fig1)
    graphs["Liens_d_amitie"] = fig1


    # Graph des inimitiés simple
    edge_data_lienmoins  = create_edge_data(df_network_lienmoins)
    edge_color_lienmoins = creat_edge_color(df_network_lienmoins)

    st.header("Liens d'inimitié")
    fig2, _ = create_directed_graph("simple", node_data_simple, edge_data_lienmoins, edge_color_lienmoins, edge_width=1, node_positions=pos)
    st.pyplot(fig2)
    graphs["Liens_d_inimitie"] = fig2

    # Graph avec cantine
    edge_data_cantine = create_edge_data(df_network_cantine)

    st.header("Liens de cantine")
    fig3, _ = create_directed_graph("simple", node_data_simple, edge_data_cantine, edge_width=1, node_positions=pos)
    st.pyplot(fig3)
    graphs["Liens_de_cantine"] = fig3

    # Graph avec orientation
    edge_data_orientation = create_edge_data(df_network_orientation)

    st.header("Liens d'orientation")
    fig4, _ = create_directed_graph("simple", node_data_simple, edge_data_orientation, edge_width=1, node_positions=pos)
    st.pyplot(fig4)
    graphs["Liens_d_orientation"] = fig4
    # Graph avec les amitiés de milieu d’année X ce qu’ils souhaitent faire en milieu d’année
    
    node_data_domaine = create_node_data_domaine(df_nom, "Dom_mi année 1", "Dom_mi année 2")

    st.header("Lien d'amitié avec choix domaine")


    fig5, _ = create_directed_graph("sector", node_data_domaine, edge_data_lienplus, edge_color_lienplus, edge_width=1, colorlist=colorlist_secteur, node_positions=pos)
    st.pyplot(fig5)
    graphs["Lien_d_amitie_choix_domaine"] = fig5

    # Graph avec les amitiés de milieu d’année X les PCS ménages

    note_data_pcs = create_node_data_type(df_nom, "PCS_Ménage")
    
    st.header("Lien d'amitié avec PCS ménage")
    fig6, _ = create_directed_graph("type", note_data_pcs, edge_data_lienplus, edge_color_lienplus, edge_width=1, colorlist=colorlist_pcs, node_positions=pos)
    st.pyplot(fig6)
    graphs["Lien_d_amitie_PCS_menage"] = fig6
    # ----------------------------------------------------------------------------------------------------------------------------
    # Graph avec les amitiés de fin d’année X domaine 
    edge_data_fin_annee = create_edge_data(df_network_fin_annee)
    edge_color_fin_annee = creat_edge_color(df_network_fin_annee)

    node_data_fin_annee = create_node_data_domaine(df_nom, "Domaine parcoursup")
    st.header("Liens d'amitié de fin d'année avec choix domaine")

    fig7, _ = create_directed_graph("sector", node_data_fin_annee, edge_data_fin_annee, edge_color_fin_annee, edge_width=1, colorlist=colorlist_secteur_fin_annee, node_positions=pos)
    st.pyplot(fig7)
    graphs["Lien_d_amitie_choix_domaine_fin_annee"] = fig7

    # Graph avec les amitiés de fin d’année X établissement

    node_data_etablissement = create_node_data_type(df_nom, "Etablissement Parcoursup")
    st.header("Liens d'amitié de fin d'année avec type établissement")

    fig8, _ = create_directed_graph("type", node_data_etablissement, edge_data_fin_annee, edge_color_fin_annee, edge_width=1, colorlist=colorlist_etablissement,node_positions=pos)
    st.pyplot(fig8)
    graphs["Lien_d_amitie_type_etablissement_fin_annee"] = fig8

    # Graph avec les amitiés de fin d’année X Hors/dans Parcoursup
    node_data_hors_dans = create_node_data_type(df_nom, "Hors/dans Parcoursup")
    st.header("Liens d'amitié de fin d'année avec Hors/dans Parcoursup")

    fig9, _ = create_directed_graph("type", node_data_hors_dans, edge_data_fin_annee, edge_color_fin_annee, edge_width=1, colorlist=colorlist_hors_dans, node_positions=pos)
    st.pyplot(fig9)
    graphs["Lien_d_amitie_Hors_dans_Parcoursup_fin_annee"] = fig9
    # ----------------------------------------------------------------------------------------------------------------------------
    # Graph des amitiés en études sup X domaine Parcoursup
    edge_data_etudes = create_edge_data(df_network_etudes)

    st.header("Liens d'amitié en études sup avec choix domaine")

    fig10, _ = create_directed_graph("sector", node_data_fin_annee, edge_data_etudes, edge_width=1, colorlist=colorlist_secteur_fin_annee   , node_positions=pos)
    st.pyplot(fig10)
    graphs["Lien_d_amitie_choix_domaine_etudes_sup"] = fig10

    # Graph des amitiés en études sup X établissement Parcoursup
    st.header("Liens d'amitié en études sup avec type établissement")

    fig11, _ = create_directed_graph("type", node_data_etablissement, edge_data_etudes, edge_width=1, colorlist=colorlist_etablissement, node_positions=pos)
    st.pyplot(fig11)
    graphs["Lien_d_amitie_type_etablissement_etudes_sup"] = fig11

    # Graph des amitiés en études sup X Hors/dans Parcoursup
    st.header("Liens d'amitié en études sup avec Hors/dans Parcoursup")

    fig12, _ = create_directed_graph("type", node_data_hors_dans, edge_data_etudes, edge_width=1, colorlist=colorlist_hors_dans, node_positions=pos)
    st.pyplot(fig12)
    graphs["Lien_d_amitie_Hors_dans_Parcoursup_etudes_sup"] = fig12

    download_graphs(graphs)


if __name__ == "__main__":
    main()