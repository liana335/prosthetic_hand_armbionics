import json
from datetime import datetime, timedelta
from user.user_info import User, Sample, Session


def save_user(user, filename):
    user.calculate_voltages()

    data = {
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "prosthesis_type": user.prosthesis_type,

        "emg1_idle_voltage": user.emg1_idle_voltage,
        "emg2_idle_voltage": user.emg2_idle_voltage,

        "emg1_active_voltage": user.emg1_active_voltage,
        "emg2_active_voltage": user.emg2_active_voltage,

        "sessions": [
            {
                "session_start": session.session_start.isoformat(),
                "session_end": (session.session_end.isoformat() if session.session_end is not None else None),

                "emg1_idle_history": session.emg1_idle_history,
                "emg2_idle_history": session.emg2_idle_history,

                "emg1_samples": [
                    {
                        "timestamp": sample.timestamp.isoformat(),
                        "sample_voltage": sample.sample_voltage,
                        "duration": sample.duration.total_seconds()
                    }
                    for sample in session.emg1_samples
                ],

                "emg2_samples": [
                    {
                        "timestamp": sample.timestamp.isoformat(),
                        "sample_voltage": sample.sample_voltage,
                        "duration": sample.duration.total_seconds()
                    }
                    for sample in session.emg2_samples
                ]
            }
            for session in user.sessions
        ]
    }

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_user(filename):
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    user = User(id=data.get("id", "000"), 
                name=data.get("name", "Anonymous"), 
                surname=data.get("surname", ""), 
                prosthesis_type=data.get("prosthesis_type", ""))

    user.emg1_idle_voltage = data.get("emg1_idle_voltage", 0)
    user.emg2_idle_voltage = data.get("emg2_idle_voltage", 0)

    user.emg1_active_voltage = data.get("emg1_active_voltage", 0)
    user.emg2_active_voltage = data.get("emg2_active_voltage", 0)

    for session_data in data.get("sessions", []):
        session_start = datetime.fromisoformat(session_data["session_start"])

        session_end = None

        if session_data.get("session_end") is not None:
            session_end = datetime.fromisoformat(session_data["session_end"])

        session = Session(
            session_start=session_start,
            session_end=session_end,
            emg1_idle_history = session_data.get("emg1_idle_history", []),
            emg2_idle_history = session_data.get("emg2_idle_history", [])
        )



        for item in session_data.get("emg1_samples", []):
            sample = Sample(
                timestamp=datetime.fromisoformat(item["timestamp"]),
                sample_voltage = item["sample_voltage"],
                duration = timedelta(seconds=item["duration"])
            )

            session.emg1_samples.append(sample)

        for item in session_data.get("emg2_samples", []):
            sample = Sample(
                timestamp=datetime.fromisoformat(item["timestamp"]),
                sample_voltage = item["sample_voltage"],
                duration = timedelta(seconds=item["duration"])
            )

            session.emg2_samples.append(sample)

        user.sessions.append(session)

    user.calculate_voltages()

    return user