import pickle
import numpy as np
import pandas as pd
import plotly.express as px

from flask import Blueprint, render_template, request, session, current_app, flash


fv_bp = Blueprint("fv", __name__, url_prefix="/fv")


SUBJECT_FILES = {
    "CTRL_1": "fv_subject_01.pkl",
    "CTRL_2": "fv_subject_02.pkl",
    "CTRL_3": "fv_subject_03.pkl",
    "CTRL_4": "fv_subject_04.pkl",
}

@fv_bp.route("/", methods=["GET", "POST"])
def view():
    data_folder = current_app.config["DATA_DIR"]

    if "current_index" not in session:
        session["current_index"] = 0
    if "patient" not in session:
        session["patient"] = "CTRL_1"
    if "sac_number" not in session:
        session["sac_number"] = 0
    if "movie_number" not in session:
        session["movie_number"] = 1

    if request.method == "POST":
        if "movie_number" in request.form:
            session["movie_number"] = int(request.form["movie_number"])
            session["sac_number"] = 0
        if "sac_number" in request.form:
            session["sac_number"] = int(request.form["sac_number"])

    action = request.form.get("action")

    if action == "forward":
        session["sac_number"] += 1
    elif action == "backward":
        session["sac_number"] -= 1
    elif action in SUBJECT_FILES:
        session["patient"] = action
        session["sac_number"] = 0

    patient = session["patient"]
    file_path = data_folder / SUBJECT_FILES[patient]

    with open(file_path, "rb") as f:
        all_subjects = pickle.load(f)

    mv_number = session["movie_number"]

    if mv_number not in all_subjects:
        first_movie = list(all_subjects.keys())[0]
        max_mv_num = max(all_subjects.keys())
        flash(f"Movie {mv_number} does not exist (max: {max_mv_num}). Showing movie {first_movie} instead.")
        mv_number = first_movie
        session["movie_number"] = mv_number
        session["sac_number"] = 0

    if session["sac_number"] > len(all_subjects[mv_number]) - 1:
        max_sacc_num = len(all_subjects[mv_number]) - 1
        flash(f"Saccade {session['sac_number']} does not exist (max: {max_sacc_num}). Showing saccade 0 instead.")
        session["sac_number"] = 0
    if session["sac_number"] < 0:
        session["sac_number"] = len(all_subjects[mv_number]) - 1

    sac_number = session["sac_number"]
    trace = all_subjects[mv_number][sac_number]

    print("FV:", patient, mv_number, sac_number)

    time = np.arange(0, len(trace) * 2, 2)

    data = pd.DataFrame({"Time": time, "X Position": trace[:, 0]})
    data2 = pd.DataFrame({"Time": time, "Y Position": trace[:, 1]})
    data3 = pd.DataFrame({"Time": time, "Velocity": trace[:, 2]})
    data4 = pd.DataFrame({"Time": time, "Acceleration": trace[:, 3]})
    data5 = pd.DataFrame({"Time": time, "X velocity": trace[:, 7]})
    data6 = pd.DataFrame({"Time": time, "Y velocity": trace[:, 8]})
    deltaDirection = pd.DataFrame({"Time": time, "Direction change": trace[:, 6] * 10})

    sac_locations = trace[:, 5]
    saccade_indices = np.where(sac_locations == 1)[0]
    st = saccade_indices[0]
    en = saccade_indices[1] - 1

    data7 = pd.DataFrame({"X Position": trace[st:en + 1, 0], "Y Position": trace[st:en + 1, 1], "Color": np.zeros(en - st + 1)})

    max_y_label_width = max(len(str(int(data["X Position"].max()))), len(str(int(data["X Position"].min()))), len(str(int(data5["X velocity"].max()))), len(str(int(data5["X velocity"].min()))), len(str(int(data6["Y velocity"].max()))), len(str(int(data6["Y velocity"].min()))))
    left_margin_size = max_y_label_width * 10

    segment_size = request.form.get("segment_size", default=500, type=int)
    session["current_index"] = max(0, min(session["current_index"], len(data) - segment_size))

    start_index = session["current_index"]
    end_index = start_index + segment_size

    fig1 = px.line(data.iloc[start_index:end_index], x="Time", y="X Position", title="X Position Over Time")
    fig1.add_vline(x=st * 2, line_dash="dot", line_color="red")
    fig1.add_vline(x=en * 2, line_dash="dot", line_color="red")
    fig1.update_layout(margin=dict(l=left_margin_size, r=20, t=30, b=20), clickmode="event+select")
    fig1.update_traces(mode="lines+markers")
    graphJSON1 = fig1.to_json()

    fig2 = px.line(data2.iloc[start_index:end_index], x="Time", y="Y Position", title="Y Position Over Time")
    fig2.add_vline(x=st * 2, line_dash="dot", line_color="red")
    fig2.add_vline(x=en * 2, line_dash="dot", line_color="red")
    fig2.update_layout(margin=dict(l=left_margin_size, r=20, t=30, b=20), clickmode="event+select")
    fig2.update_traces(mode="lines+markers")
    graphJSON2 = fig2.to_json()

    fig3 = px.line(data3.iloc[start_index:end_index], x="Time", y="Velocity", title="Velocity Over Time")
    fig3.data[0].name = "XY velocity"
    fig3.data[0].showlegend = True
    fig3.add_vline(x=st * 2, line_dash="dot", line_color="red")
    fig3.add_vline(x=en * 2, line_dash="dot", line_color="red")

    line2 = px.line(deltaDirection.iloc[start_index:end_index], x="Time", y="Direction change")
    line2.data[0].name = "Direction change"
    line2.data[0].line.color = "green"
    line2.data[0].showlegend = True

    for trace2 in line2.data:
        fig3.add_trace(trace2)

    fig3.update_layout(margin=dict(l=left_margin_size, r=20, t=30, b=20), clickmode="event+select", legend=dict(x=1, y=1, xanchor="right", yanchor="top"))
    fig3.update_traces(mode="lines+markers")
    graphJSON3 = fig3.to_json()

    fig4 = px.line(data5.iloc[start_index:end_index], x="Time", y="X velocity", title="X and Y Velocity Over Time")
    fig4.data[0].name = "X velocity"
    fig4.data[0].showlegend = True
    fig4.data[0].line.color = "green"

    line2 = px.line(data6.iloc[start_index:end_index], x="Time", y="Y velocity")
    line2.data[0].name = "Y velocity"
    line2.data[0].showlegend = True

    for trace2 in line2.data:
        fig4.add_trace(trace2)

    fig4.add_vline(x=st * 2, line_dash="dot", line_color="red")
    fig4.add_vline(x=en * 2, line_dash="dot", line_color="red")
    fig4.update_layout(margin=dict(l=left_margin_size, r=20, t=30, b=20), legend=dict(x=1, y=1, xanchor="right", yanchor="top"), clickmode="event+select", yaxis_title="X and Y velocity")
    fig4.update_traces(mode="lines+markers")
    graphJSON4 = fig4.to_json()

    fig5 = px.line(data4.iloc[start_index:end_index], x="Time", y="Acceleration", title="Acceleration Over Time")
    fig5.add_vline(x=st * 2, line_dash="dot", line_color="red")
    fig5.add_vline(x=en * 2, line_dash="dot", line_color="red")
    fig5.update_layout(margin=dict(l=left_margin_size, r=20, t=30, b=20), clickmode="event+select")
    fig5.update_traces(mode="lines+markers")
    graphJSON5 = fig5.to_json()

    fig6 = px.scatter(data7, x="X Position", y="Y Position", title="Y Position vs X Position")
    fig6.update_layout(margin=dict(l=left_margin_size, r=20, t=30, b=20), clickmode="event+select")
    fig6.update_traces(mode="lines+markers")
    graphJSON6 = fig6.to_json()

    fig7 = px.scatter(data7, x="X Position", y="Y Position", title="Saccade Zoomed Out")
    fig7.update_layout(margin=dict(l=left_margin_size, r=20, t=30, b=20), clickmode="event+select")
    fig7.update_traces(mode="lines+markers")
    graphJSON7 = fig7.to_json()

    return render_template("index_FV.html", graphJSON1=graphJSON1, graphJSON2=graphJSON2, graphJSON3=graphJSON3, graphJSON4=graphJSON4, graphJSON5=graphJSON5, graphJSON6=graphJSON6, graphJSON7=graphJSON7, segment_size=segment_size)