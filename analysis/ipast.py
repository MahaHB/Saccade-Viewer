import os
import pickle
import numpy as np
import pandas as pd
import plotly.express as px

from flask import Blueprint, render_template, request, session, current_app, flash
from utils.IPASTStats import IPASTStats


ipast_bp = Blueprint("ipast", __name__, url_prefix="/ipast")




SUBJECT_FILES = {
    "CTRL_1": "ipast_subject_01",
    "CTRL_2": "ipast_subject_02",
    "CTRL_3": "ipast_subject_03",
    "CTRL_4": "ipast_subject_04"
}

@ipast_bp.route("/", methods=["GET", "POST"])
def view():

    data_folder = current_app.config["DATA_DIR"]

    if 'block_number' not in session:
        session['block_number'] = 1
    if 'current_index' not in session:
        session['current_index'] = 0
    if 'patient' not in session:
        session['patient'] = 'CTRL_1'
    if 'sac_number' not in session:
        session['sac_number'] = 0
    if 'trial_number' not in session:
        session['trial_number'] = 0

    requested_trial = None

    if request.method == 'POST':
        if 'sac_number' in request.form:
            session['sac_number'] = int(request.form['sac_number'])

        if 'trial_number' in request.form:
            requested_trial = int(request.form['trial_number'])
            session['trial_number'] = requested_trial
            session['sac_number'] = 0

    action = request.form.get('action')

    if action == 'forward':
        session['sac_number'] += 1
    elif action == 'backward':
        session['sac_number'] -= 1
    elif action in SUBJECT_FILES:
        session['patient'] = action
        session['block_number'] = 1
        session['trial_number'] = 0
        session['sac_number'] = 0
    elif action == 'Previous_trial':
        if session['trial_number'] > 0:
            session['trial_number'] -= 1
        session['sac_number'] = 0
    elif action == 'Next_trial':
        session['trial_number'] += 1
        session['sac_number'] = 0



    subject_file = SUBJECT_FILES[session['patient']]
    block_number = session['block_number']
    file_path = data_folder / f"{subject_file}_b{block_number:02d}.pkl"


    with open(file_path, 'rb') as f:
        all_subjects = pickle.load(f)

    if requested_trial is not None:
        max_trial = len(all_subjects['trial_data']) - 1
        if requested_trial < 0 or requested_trial > max_trial:
            flash(f"Trial {requested_trial} does not exist. Valid trials are 0–{max_trial}. Showing trial 0 instead.")
            session['trial_number'] = 0

    if session['trial_number'] > len(all_subjects['trial_data']) - 1:
        next_block = session['block_number'] + 1

        next_file = data_folder / f"{subject_file}_b{next_block:02d}.pkl"

        if os.path.exists(next_file):
            session['block_number'] = next_block
            session['trial_number'] = 0

            with open(next_file, 'rb') as f:
                all_subjects = pickle.load(f)
        else:
            session['trial_number'] = 0

    mv_number = session[
        'trial_number']

    if 'sac_number' not in session:
        session['sac_number'] = 0


    # check if sac_number is not out of range
    if session['sac_number'] > len(all_subjects['trial_data'][mv_number]['sac_trace']) - 1:
        session['sac_number'] = 0
        session['trial_number'] += 1
        if session['trial_number'] > len(all_subjects['trial_data']) - 1:
            session['trial_number'] = 0
        mv_number = session['trial_number']

    if session['sac_number'] < 0:
        session['trial_number'] -= 1
        if session['trial_number'] < 0:
            session['trial_number'] = len(all_subjects['trial_data']) - 1
        mv_number = session['trial_number']
        session['sac_number'] = len(all_subjects['trial_data'][mv_number]['sac_trace']) - 1

    sac_number = session['sac_number']
    print(mv_number, sac_number)
    time = np.arange(0, len(all_subjects['trial_data'][mv_number]['sac_trace'][sac_number][:, 2]) * 2, 2)

    data = pd.DataFrame(
        {'Time': time, 'X Position': all_subjects['trial_data'][mv_number]['sac_trace'][sac_number][:, 0]})
    data2 = pd.DataFrame(
        {'Time': time, 'Y Position': all_subjects['trial_data'][mv_number]['sac_trace'][sac_number][:, 1]})
    data3 = pd.DataFrame(
        {'Time': time, 'Velocity': all_subjects['trial_data'][mv_number]['sac_trace'][sac_number][:, 2]})
    data4 = pd.DataFrame(
        {'Time': time, 'Acceleration': all_subjects['trial_data'][mv_number]['sac_trace'][sac_number][:, 3]})
    data5 = pd.DataFrame(
        {'Time': time, 'X velocity': all_subjects['trial_data'][mv_number]['sac_trace'][sac_number][:, 7]})
    data6 = pd.DataFrame(
        {'Time': time, 'Y velocity': all_subjects['trial_data'][mv_number]['sac_trace'][sac_number][:, 8]})
    deltaDirection = pd.DataFrame({'Time': time, 'Direction change':
        all_subjects['trial_data'][mv_number]['sac_trace'][sac_number][:, 6] * 10})
    task = all_subjects['trial_events_table']['task'][mv_number]


    mark_value = all_subjects['trial_data'][mv_number]['saccades'][sac_number]['mark']
    if mark_value:
        sacc_marks = [key for key, value in IPASTStats.sacc_marks.items() if value == mark_value]
    else:
        sacc_marks = ['Unknown']

    sac_locations = all_subjects['trial_data'][mv_number]['sac_trace'][sac_number][:, 5]
    saccade_indices = np.where(sac_locations == 1)[0]
    st = saccade_indices[0]
    en = saccade_indices[1] - 1
    data7 = pd.DataFrame(
        {'X Position': all_subjects['trial_data'][mv_number]['sac_trace'][sac_number][st:en + 1, 0],
         'Y Position': all_subjects['trial_data'][mv_number]['sac_trace'][sac_number][st:en + 1, 1],
         'Color': np.zeros(en - st + 1)})

    # Calculate the width of the y-axis labels
    max_y_label_width = max(len(str(int(data['X Position'].max()))), len(str(int(data['X Position'].min()))),
                            len(str(int(data5['X velocity'].max()))), len(str(int(data5['X velocity'].min()))),
                            len(str(int(data6['Y velocity'].max()))), len(str(int(data6['Y velocity'].min()))))

    left_margin_size = max_y_label_width * 10
    segment_size = request.form.get('segment_size', default=500, type=int)


    session['current_index'] = max(0, min(session['current_index'], len(data) - segment_size))

    start_index = session['current_index']
    end_index = start_index + segment_size


    fig1 = px.line(data.iloc[start_index:end_index], x='Time', y='X Position', title='X Position Over Time')
    fig1.add_vline(x=st * 2, line_dash="dot", line_color="red")
    fig1.add_vline(x=en * 2, line_dash="dot", line_color="red")


    fig1.update_layout(margin=dict(l=left_margin_size, r=20, t=30, b=20), clickmode='event+select')
    fig1.update_traces(mode='lines+markers')
    graphJSON1 = fig1.to_json()

    # NoTE: figure 2
    fig2 = px.line(data2.iloc[start_index:end_index], x='Time', y='Y Position', title='Y Position Over Time')
    fig2.add_vline(x=st * 2, line_dash="dot", line_color="red")
    fig2.add_vline(x=en * 2, line_dash="dot", line_color="red")

    fig2.update_layout(margin=dict(l=left_margin_size, r=20, t=30, b=20), clickmode='event+select')
    fig2.update_traces(mode='lines+markers')
    graphJSON2 = fig2.to_json()

    # NoTE: figure 3
    fig3 = px.line(data3.iloc[start_index:end_index], x='Time', y='Velocity', title='Velocity Over Time')
    fig3.data[0].name = 'XY velocity'
    fig3.data[0].showlegend = True
    fig3.update_traces(mode='lines+markers')
    fig3.add_vline(x=st * 2, line_dash="dot", line_color="red")
    fig3.add_vline(x=en * 2, line_dash="dot", line_color="red")

    line2 = px.line(deltaDirection[start_index:end_index], x='Time', y='Direction change')
    line2.data[0].name = 'Direction change'
    line2.data[0].line.color = 'green'
    line2.data[0].showlegend = True
    for trace in line2.data:
        fig3.add_trace(trace)

    fig3.update_layout(margin=dict(l=left_margin_size, r=20, t=30, b=20), clickmode='event+select', legend=dict(
        x=1,
        y=1,
        xanchor='right',
        yanchor='top'), )
    graphJSON3 = fig3.to_json()
    # NoTE: figure 4
    fig4 = px.line(data5.iloc[start_index:end_index], x='Time', y='X velocity', title='X and Y Velocity Over Time')
    fig4.data[0].name = 'X velocity'
    fig4.data[0].showlegend = True
    fig4.data[0].line.color = 'green'

    line2 = px.line(data6.iloc[start_index:end_index], x='Time', y='Y velocity')
    line2.data[0].name = 'Y velocity'
    line2.data[0].showlegend = True
    for trace in line2.data:
        fig4.add_trace(trace)
    fig4.add_vline(x=st * 2, line_dash="dot", line_color="red")
    fig4.add_vline(x=en * 2, line_dash="dot", line_color="red")

    fig4.update_layout(margin=dict(l=left_margin_size, r=20, t=30, b=20),
                       legend=dict(
                           x=1,
                           y=1,
                           xanchor='right',
                           yanchor='top'),
                       clickmode='event+select', yaxis_title='X and Y velocity')
    fig4.update_traces(mode='lines+markers')
    graphJSON4 = fig4.to_json()
    # NoTE: figure 5
    # Plot for data4
    fig5 = px.line(data4.iloc[start_index:end_index], x='Time', y='Acceleration', title='Acceleration Over Time')
    fig5.add_vline(x=st * 2, line_dash="dot", line_color="red")
    fig5.add_vline(x=en * 2, line_dash="dot", line_color="red")
    fig5.update_layout(margin=dict(l=left_margin_size, r=20, t=30, b=20), clickmode='event+select')
    fig5.update_traces(mode='lines+markers')
    graphJSON5 = fig5.to_json()

    # NoTE: figure 6

    title_text = (f'Trial: {mv_number}    {task}: {sacc_marks[0]}')

    width = 4
    height = 2
    rec_loc = all_subjects['trial_events_table']['corr_loc_to_look'][mv_number]
    bottom_left_x = rec_loc - width / 2
    bottom_left_y = 0 - height / 2

    fig6 = px.scatter(data7, x='X Position', y='Y Position',
                      title=title_text)
    fig6.add_shape(
        type="rect",
        x0=bottom_left_x,
        y0=bottom_left_y,
        x1=bottom_left_x + width,
        y1=bottom_left_y + height,
        line=dict(color="blue"),
        fillcolor="blue",
        opacity=0.5,
    )
    col = 'green' if task == 'prosaccade' else 'red'
    fig6.add_shape(
        type="circle",
        x0=-1, y0=-1, x1=1, y1=1,
        line=dict(color=col),
        fillcolor=col,
        opacity=0.5,
        xref="x", yref="y"
    )
    fig6.update_xaxes(range=[-20, 20])
    fig6.update_yaxes(range=[-10, 10])


    fig6.update_layout(margin=dict(l=left_margin_size, r=20, t=30, b=20), clickmode='event+select')
    fig6.update_traces(mode='lines+markers')
    graphJSON6 = fig6.to_json()
    # NoTE: figure 7

    fig7 = px.scatter(data7, x='X Position', y='Y Position',
                      title='Y Position vs X Position')


    fig7.update_layout(margin=dict(l=left_margin_size, r=20, t=30, b=20), clickmode='event+select')
    fig7.update_traces(mode='lines+markers')
    graphJSON7 = fig7.to_json()

    return render_template('index_IPAST.html', graphJSON1=graphJSON1, graphJSON2=graphJSON2, graphJSON3=graphJSON3,
                           graphJSON4=graphJSON4, graphJSON5=graphJSON5, graphJSON6=graphJSON6,
                           graphJSON7=graphJSON7, segment_size=segment_size)