# NOTES:
# https://plotly.com/python/mapbox-layers/ (example used)
import plotly.graph_objects as go
import plotly.express as px

def generate_geo_plot(df, zoom, size, heatmap_enabled, token):
    fig = None
    if not heatmap_enabled:
        fig = px.scatter_mapbox(df, hover_name="Name",
                                lat="Latitude", lon="Longitude",
                                hover_data=["Date/Time UTC", "Course Behavior",
                                "Max Speed kn", "Mean Speed kn", "WSPD mph", "LOA ft"],
                                color_discrete_sequence=["white"],
                                zoom=zoom, height=size[0], width=size[1])
        fig.update_traces(marker_size=4)
    else:
        fig = px.density_mapbox(df, hover_name="Name",
                                z="Max Speed kn", radius=5,
                                lat="Latitude", lon="Longitude",
                                hover_data=["Date/Time UTC", "Course Behavior",
                                "Max Speed kn", "Mean Speed kn", "WSPD mph", "LOA ft"],
                                zoom=zoom, height=size[0], width=size[1])
    fig.update_layout(mapbox_accesstoken=token,
                      mapbox_style="satellite-streets", showlegend=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

def generate_vspd_hist(df):
    fig = px.histogram(df, x="VSPD kn", color="Transit", nbins=20, color_discrete_sequence=["darkslateblue", "#ab63eb"])
    fig.update_layout(barmode="overlay",
                       xaxis_title_text = "VSPD kn",
                       yaxis_title_text = "Unique AIS Positions",
                       title = "Vessl Speed Histogram" '<br>'
                               "Compliance Rate: " + str(round(sum(df["VSPD kn"] <= 10) / df.shape[0] * 100, 2)) + "%" "<br>"
                               "Mean VSPD: " + str(round(df["VSPD kn"].mean(), 2)) + " kn",
                       showlegend = True, hoverlabel=dict(bgcolor="white",
                                         font_size=13),
                       legend_title_text="",
                       width=900,
                       height=600,
                       plot_bgcolor="#F1F1F1",
                       font=dict(size=12),
                       titlefont=dict(size=12))
    fig.add_shape(type="line", x0=10, y0=0, x1=10, y1=1, xref="x", yref="paper",
                    line=dict(color="Red", dash="solid", width=1.5))
    fig.add_shape(type="line", x0=df["VSPD kn"].mean(), y0=0, x1=df["VSPD kn"].mean(), y1=1,
                   xref="x", yref="paper",
                   line=dict(color="black", dash="dash", width=1.5))
    fig.add_annotation(text="Speed Limit", showarrow=False, textangle=90, font=dict(color="red"),
                        xref="x", x=10.15, yref="paper", y=1)
    fig.add_annotation(text="Mean", showarrow=False, textangle=90, font=dict(color="black"),
                        xref="x", x=df["VSPD kn"].mean()+0.15, yref="paper", y=1,
                        hovertext=str(round(df["VSPD kn"].mean(), 2)))
    fig.data[0].marker.line.width = 0.5
    fig.data[0].marker.line.color = "black"
    fig.data[1].marker.line.width = 0.5
    fig.data[1].marker.line.color = "black"
    return fig

def generate_wspd_hist(df_dropna):
    fig = px.histogram(df_dropna["WSPD mph"], color_discrete_sequence=["lightsteelblue"], nbins=15)
    fig.add_shape(go.layout.Shape(type="line", xref="x", yref="paper",
                            x0=30, y0=0, x1=30, y1=1, line={"dash": "solid", "width":1.5}))
    fig.update_layout(title= "Windspeed Histogram" '<br>'
                             "Adverse Wind Conditions: " + str(round((df_dropna[df_dropna["WSPD mph"] >= 30].shape[0] / df_dropna.shape[0]) * 100, 2)) + "% ",
                      xaxis_title_text="WSPD mph", yaxis_title_text="Unique AIS Positions",
                      showlegend = False, hoverlabel=dict(bgcolor="white",font_size=13),
                      width=900,
                      height=600,
                      plot_bgcolor="#F1F1F1",
                      font=dict(size=12),
                      titlefont=dict(size=14))
    fig.add_annotation(text="Adverse WSPD Threshold", showarrow=False, textangle=90, font=dict(color="black"),
                        xref="x", x=30.4, yref="paper", y=1)
    fig.data[0].marker.line.width = 0.5
    fig.data[0].marker.line.color = "black"
    return fig

def generate_wspd_vs_vspd(df_dropna):
    fig = px.density_contour(df_dropna, x="VSPD kn", y="WSPD mph")
    fig.update_traces(contours_coloring = "fill", colorscale = "blues")
    fig.update_layout(xaxis_title_text = "VSPD kn",
                      title= "Wind and Vessel Speed Density Plot" '<br>'
                             "WSPD-VSPD Correlation: " + str(round(df_dropna[["VSPD kn", "WSPD mph"]].corr().iloc[0][1] * 100, 2)) + "%",
                       hoverlabel=dict(bgcolor="white", font_size=13),
                       width=900,
                       height=600,
                       plot_bgcolor="#F1F1F1",
                       font=dict(size=12),
                       titlefont=dict(size=14))
    return fig

def generate_strip_plot(df):
    hover_dict = {"Date/Time UTC":True, "MMSI":False, "VSPD kn":True, "WSPD mph":True, "Course Behavior":True,
                  "Yaw":True, "LOA ft":False, "Beam ft":False, "Effective Beam ft":True,
                  "Location":False, "Name":False}
    fig = px.strip(df, x="Name", y="VSPD kn",
                    color="Transit", hover_data=hover_dict, hover_name="Name", stripmode="overlay",
                    color_discrete_sequence=["darkslateblue", "#ab63eb"], width=900, height=600,
                    title= "Vessel Speed Plot: One Minute Time Resolution" '<br>'
                           "One Way Transits: " + str(round((df[df.Transit == "One Way Transit"].shape[0] / df.shape[0]) * 100, 2)) + "%" "<br>"
                           "Two Way Transits: " + str(round((df[df.Transit == "Two Way Transit"].shape[0] / df.shape[0]) * 100, 2)) + "%")
    fig.add_shape(type="line", x0=0, y0=10, x1=1, y1=10, xref="paper", yref="y",
                    line=dict(color="Red", dash="solid", width=1.5))
    fig.update_layout(xaxis_title_text = "",
                      hoverlabel=dict(bgcolor="white",
                                        font_size=13),
                      legend_title_text="",
                       width=900,
                       height=650,
                       plot_bgcolor="#F1F1F1",
                       font=dict(size=12),
                       titlefont=dict(size=14))
    fig.update_traces(marker_size=4)
    return fig

def generate_line_plot(df):
    t1 = go.Scatter(x=df.index, y=df["VSPD kn"], mode="lines", name="VSPD kn", line=dict(width=1.5, color="#1f77b4"), hoverinfo="skip")
    t2 = go.Scatter(x=df.index, y=df["Yaw"], mode="lines", name="Yaw deg", line=dict(width=1.5, color="#9467bd"), hoverinfo="skip")
    fig = go.Figure(data=[t1, t2])
    fig.update_layout(title="Vessel Speed and Yaw Line Plot" '<br>'
                             "VSPD-Yaw Correlation: " + str(round(df.dropna()[["VSPD kn", "Yaw"]].corr().iloc[0][1], 2)) + "<br>"
                             "Compliant Yaw (Mean): " + str(round(df[df["VSPD kn"] <= 10].Yaw.mean(), 2)) + " deg" + "<br>"
                             "Non Compliant Yaw (Mean):  " + str(round(df[df["VSPD kn"] > 10].Yaw.mean(), 2)) + " deg",
                      xaxis_title_text="Unique AIS Positions",
                      width=900,
                      height=600,
                      plot_bgcolor="#F1F1F1",
                      font=dict(size=12),
                      titlefont=dict(size=12.5))
    return fig

def generate_channel_occ(df):
    hover_dict = {"Date/Time UTC":True, "MMSI":False, "VSPD kn":True, "WSPD mph":True, "Course Behavior":True,
                  "Yaw":True, "LOA ft":False, "Beam ft":False, "Effective Beam ft":True,
                  "Location":False, "Name":False}
    # fig = px.scatter(df[(df["Transit"] == "One Way Transit") & (df["WSPD mph"] < 30)], x="VSPD kn", y="% Channel Occupied", hover_data=hover_dict,
    #                          color_discrete_sequence=["darkslateblue", "salmon"], width=800, height=500,
    #                          title="Non Adverse Conditions: " + str(round(len(df[(df["Transit"] == "One Way Transit") & (df["WSPD mph"] < 30)]) / len(df) * 100, 2)) + "%")
    # fig = px.density_contour(df[(df["Transit"] == "One Way Transit") & (df["WSPD mph"] < 30)], x="VSPD kn", y="% Channel Occupied", width=800, height=500, hover_data=hover_dict,
    #                          title= "VSPD-Occupied Channel Desntiy Plot" '<br>'
    #                                 "Non Adverse Conditions: " + str(round(len(df[(df["Transit"] == "One Way Transit") & (df["WSPD mph"] < 30)]) / len(df) * 100, 2)) + "%")
    fig = px.density_heatmap(df[(df["Transit"] == "One Way Transit") & (df["WSPD mph"] < 30)], x="VSPD kn", y="% Channel Occupied",
                            width=800, height=500, hover_data=hover_dict,
                            color_continuous_scale="greens",
                            nbinsx=20, nbinsy=20, #color_continuous_midpoint=20,
                             title= "Vessel Speed and Occupied Channel Heatmap" '<br>'
                                    "Non Adverse Conditions: " + str(round(len(df[(df["Transit"] == "One Way Transit") & (df["WSPD mph"] < 30)]) / len(df) * 100, 2)) + "%")
    # fig.update_traces(contours_coloring = "fill", colorscale = "greens")
    # fig.add_shape(type="line", x0=20, y0=0, x1=20, y1=1, xref="x", yref="paper",
    #                 line=dict(color="Red", dash="solid", width=1.5))
    fig.add_shape(type="line", x0=0, y0=20, x1=1, y1=20, xref="paper", yref="y",
                    line=dict(color="Red", dash="solid", width=1.5))
    fig.update_layout(width=900,
                      height=600,
                      plot_bgcolor="#F1F1F1",
                      font=dict(size=12),
                      titlefont=dict(size=14))
    return fig
