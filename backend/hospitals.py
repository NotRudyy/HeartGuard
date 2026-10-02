"""Hospital list. Format: "Name|G or P|1 if dedicated heart institute else 0".
G = government, P = private. Add or edit freely. Phone numbers are intentionally not stored:
add a fourth field once you have verified numbers."""

RAW = {
    "Delhi": {"New Delhi": ["AIIMS New Delhi|G|0", "Fortis Escorts Heart Institute|P|1", "Max Super Speciality Hospital, Saket|P|0"]},
    "Maharashtra": {
        "Mumbai": ["Lilavati Hospital|P|0", "Kokilaben Dhirubhai Ambani Hospital|P|0", "Nanavati Max Hospital|P|0"],
        "Pune": ["Ruby Hall Clinic|P|0", "Jehangir Hospital|P|0", "Sunshine Hospital|P|1", "Sahyadri Super Speciality Hospital|P|0"],
        "Nagpur": ["AIIMS Nagpur|G|0", "Kingsway Hospital|P|0"]},
    "Karnataka": {
        "Bengaluru": ["Sri Jayadeva Institute of Cardiovascular Sciences|G|1", "Narayana Institute of Cardiac Sciences|P|1", "Manipal Hospital|P|0"],
        "Mysuru": ["JSS Hospital|P|0", "Apollo BGS Hospital|P|0"]},
    "Tamil Nadu": {
        "Chennai": ["Apollo Hospitals, Greams Road|P|0", "MIOT International|P|0", "Fortis Malar Hospital|P|0"],
        "Coimbatore": ["PSG Hospitals|P|0", "Kovai Medical Center and Hospital|P|0"]},
    "Telangana": {"Hyderabad": ["Apollo Hospitals, Jubilee Hills|P|0", "CARE Hospitals|P|0", "Yashoda Hospitals|P|0", "NIMS Hyderabad|G|0"]},
    "Gujarat": {
        "Ahmedabad": ["U.N. Mehta Institute of Cardiology|G|1", "Apollo Hospitals International|P|0", "Zydus Hospital|P|0"],
        "Vadodara": ["SSG Hospital|G|0", "Sterling Hospital|P|0"]},
    "West Bengal": {"Kolkata": ["RN Tagore Hospital|P|1", "Medica Superspecialty Hospital|P|0", "Apollo Gleneagles Hospital|P|0", "AMRI Hospital, Dhakuria|P|0"]},
    "Uttar Pradesh": {
        "Lucknow": ["SGPGIMS|G|0", "KGMU|G|0", "Medanta Hospital Lucknow|P|0"],
        "Noida": ["Fortis Hospital Noida|P|0", "Jaypee Hospital|P|0"]},
    "Haryana": {"Gurugram": ["Medanta - The Medicity|P|0", "Fortis Memorial Research Institute|P|0"]},
    "Rajasthan": {"Jaipur": ["SMS Hospital|G|0", "Fortis Escorts Hospital|P|0", "Eternal Heart Care Centre|P|1"]},
    "Kerala": {
        "Kochi": ["Amrita Hospital|P|0", "Aster Medcity|P|0", "Lisie Hospital|P|0"],
        "Thiruvananthapuram": ["SCTIMST|G|1", "KIMS Health|P|0"]},
    "Punjab & Chandigarh": {"Chandigarh": ["PGIMER|G|0", "Fortis Hospital Mohali|P|0"]},
    "Madhya Pradesh": {
        "Bhopal": ["AIIMS Bhopal|G|0", "Bansal Hospital|P|0"],
        "Indore": ["CHL Hospital|P|0", "Choithram Hospital|P|0"]},
    "Bihar": {"Patna": ["IGIMS|G|0", "Paras HMRI Hospital|P|0"]},
    "Odisha": {"Bhubaneswar": ["AIIMS Bhubaneswar|G|0", "Apollo Hospitals|P|0", "KIMS Hospital|P|0"]},
    "Assam": {"Guwahati": ["GNRC Hospital|P|0", "Gauhati Medical College Hospital|G|0"]},
}


def parse(entry):
    name, kind, heart = entry.split("|")
    return {"name": name, "gov": kind == "G", "heart": heart == "1"}


HOSPITALS = {s: {c: [parse(e) for e in lst] for c, lst in cs.items()} for s, cs in RAW.items()}
