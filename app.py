import streamlit as st
import json
from datetime import datetime

st.set_page_config(page_icon=":material/genres:", page_title="Competition Schedule")
st.title("Competition Schedule")

time_format = "%H:%M"
date_format = "%Y-%m-%d"


@st.cache_data(show_spinner=False)
def get_schedule() -> dict:
    with open("dance_schedule.json", "r") as sch:
        return json.loads(sch.read())


@st.cache_data(show_spinner=False)
def get_awards() -> dict:
    with open("awards_schedule.json", "r") as sch:
        return json.loads(sch.read())


if current_dancer := st.query_params.get("dancer"):
    st.session_state["dancer"] = current_dancer
qry_opt = []
if "Show Awards" in st.query_params:
    qry_opt.append("Show Awards")
if "Include Production" in st.query_params:
    qry_opt.append("Include Production")
if qry_opt:
    st.session_state["options"] = qry_opt
schedule_data = get_schedule()
awards_schedule = get_awards()


dancer_names = []
dancers = [dancer_names.extend(i.get("dancers")) for i in schedule_data]

dancer_names = sorted([i for i in set(dancer_names) if i != "Production"])


def set_qp():
    if st.session_state["dancer"]:
        st.query_params["dancer"] = st.session_state["dancer"]
    else:
        if "dancer" in st.query_params:
            del st.query_params["dancer"]

    options = ["Include Production", "Show Awards"]
    for i in options:
        if i in st.session_state["options"]:
            st.query_params[i] = True
        else:
            if i in st.query_params:
                del st.query_params[i]


def render_item(performance: dict) -> None:
    st.subheader(
        f""":material/genres: {performance.get("name")}""",
        anchor=False,
    )
    st.badge(str(performance.get("id")), color="primary", icon=":material/numbers:")
    arrival_time = datetime.strptime(
        performance.get("arrival_time"), time_format
    ).strftime("%I:%M %p")

    performance_time = datetime.strptime(
        performance.get("performance_time"), time_format
    ).strftime("%I:%M %p")

    st.write(
        f""":material/check: {arrival_time} |  :material/schedule: {performance_time}"""
    )
    st.write(f"")
    st.write(
        " , ".join([f":primary-background[{i}]" for i in performance.get("dancers")])
    )


dancer = st.selectbox(
    "Choose a Dancer", options=dancer_names, key="dancer", on_change=set_qp, index=None
)
options = st.segmented_control(
    "",
    label_visibility="collapsed",
    options=["Include Production", "Show Awards"],
    selection_mode="multi",
    key="options",
    on_change=set_qp,
)


tab_elements = ["Performances"]
if "Show Awards" in options:
    tab_elements.extend(["Awards"])

if dancer:
    tabs = st.tabs(tab_elements)
    with tabs[0]:
        filtered_data = [i for i in schedule_data if dancer in i.get("dancers")]
        if "Include Production" in options:
            filtered_data.extend(
                [i for i in schedule_data if "Production" in i.get("dancers")]
            )
        filtered_data = sorted(filtered_data, key=lambda x: x.get("id"))
        dates = sorted([i for i in set([i.get("date") for i in filtered_data])])
        for d in dates:
            date_based = [i for i in filtered_data if i.get("date") == d]
            perf_date = datetime.strptime(d, date_format).date().strftime("%B %d, %Y")
            st.header(perf_date, anchor=False, divider="grey")
            for performance in date_based:
                with st.container(border=True):
                    render_item(performance=performance)
    if "Show Awards" in options:
        with tabs[1]:
            award_dates = [i for i in set([i.get("date") for i in awards_schedule])]
            for a_date in award_dates:
                a_date_set = [i for i in awards_schedule if i.get("date") == a_date]
                award_date = (
                    datetime.strptime(a_date, date_format).date().strftime("%B %d, %Y")
                )
                st.header(award_date, anchor=False, divider="grey")
                for award in a_date_set:
                    st.subheader(award.get("name"), anchor=False)
                    st.badge(
                        datetime.strptime(award.get("time"), time_format).strftime(
                            "%I:%M %p"
                        ),
                        icon=":material/schedule:",
                        color="primary",
                    )
else:
    st.info("Select Dancer to Continue...")
