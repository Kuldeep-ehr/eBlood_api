from pydantic import BaseModel, Field
from typing import Optional, List


class ComponentVolume(BaseModel):
    vol: Optional[str] = None


class ComponentDetail(BaseModel):
    component: Optional[str] = None
    unit: Optional[str] = None
    volume_normal: Optional[str] = None
    volume: Optional[List[str]] = None
    volumes: Optional[List[ComponentVolume]] = None
    req_date: Optional[str] = None
    req_comp_id: Optional[int] = None


class BloodRequestForm(BaseModel):
    request_date: Optional[str] = None
    request_order_id: Optional[str] = None
    request_number: Optional[str] = None
    request_prefix: Optional[str] = None
    request_id: Optional[str] = None
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    father_name: Optional[str] = None
    lastName: Optional[str] = None
    firstName: Optional[str] = None
    password: Optional[str] = None
    blood_request_type: Optional[str] = None
    patient_address_line1: Optional[str] = None
    patient_city: Optional[str] = None
    patient_pincode: Optional[str] = None
    patient_state: Optional[str] = None
    age: Optional[str] = None
    age_type: Optional[str] = None
    gender: Optional[str] = None
    patient_relation: Optional[str] = None
    refrence: Optional[str] = None
    hospital_name: Optional[str] = None
    hospital_mobile: Optional[str] = None
    hospital_id: Optional[int] = None
    hopsital_address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    doctor_name: Optional[str] = None
    clinical_history: Optional[str] = None
    blood_group: Optional[str] = None
    transfusion_history: Optional[str] = None
    sample_id: Optional[str] = None
    blood_require_date: Optional[str] = None
    request_type: Optional[str] = None
    sample_date: Optional[str] = None
    mother_name: Optional[str] = None
    diagnosis: Optional[str] = None
    relation: Optional[str] = None
    is_aliqout: Optional[bool] = None
    aliqout_method: Optional[str] = None
    transfusion_reason: Optional[str] = None
    thalassemia_id: Optional[str] = None
    searchfor: Optional[str] = None
    attendee_name: Optional[str] = None
    attendee_relation: Optional[str] = None
    attendee_mobile: Optional[str] = None
    ward_number: Optional[str] = None
    bed_number: Optional[str] = None
    cross_match_for: Optional[int] = None
    component_details: Optional[List[ComponentDetail]] = None


VALID_FIELDS = [
    "request_date", "request_order_id", "request_number", "request_prefix",
    "request_id", "patient_id", "patient_name", "father_name", "lastName",
    "firstName", "password", "blood_request_type", "patient_address_line1",
    "patient_city", "patient_pincode", "patient_state", "age", "age_type",
    "gender", "patient_relation", "refrence", "hospital_name", "hospital_mobile",
    "hospital_id", "hopsital_address", "city", "district", "state",
    "doctor_name", "clinical_history", "blood_group", "transfusion_history",
    "sample_id", "blood_require_date", "request_type", "sample_date",
    "mother_name", "diagnosis", "relation", "is_aliqout", "aliqout_method",
    "transfusion_reason", "thalassemia_id", "searchfor", "attendee_name",
    "attendee_relation", "attendee_mobile", "ward_number", "bed_number",
    "cross_match_for", "component_details",
]

REQUIRED_FIELDS = [
    "request_date", "request_number", "patient_name", "blood_request_type",
    "age", "gender", "hospital_name", "hopsital_address", "city",
    "district", "state", "blood_require_date", "request_type", "sample_date",
]

FIELD_LABELS = {
    "request_date": "Request Date",
    "request_order_id": "Request Order ID",
    "request_number": "Request Number",
    "request_prefix": "Request Prefix",
    "request_id": "Request ID",
    "patient_id": "Patient ID",
    "patient_name": "Patient Name",
    "father_name": "Father's Name",
    "lastName": "Last Name",
    "firstName": "First Name",
    "password": "Password",
    "blood_request_type": "Blood Request Type (1=Adult, 2=Neonatal)",
    "patient_address_line1": "Patient Address",
    "patient_city": "Patient City",
    "patient_pincode": "Patient Pincode",
    "patient_state": "Patient State",
    "age": "Age",
    "age_type": "Age Type (Y/M/D)",
    "gender": "Gender",
    "patient_relation": "Patient Relation",
    "refrence": "Reference",
    "hospital_name": "Hospital Name",
    "hospital_mobile": "Hospital Mobile/Phone",
    "hospital_id": "Hospital ID",
    "hopsital_address": "Hospital Address",
    "city": "City",
    "district": "District",
    "state": "State",
    "doctor_name": "Doctor Name",
    "clinical_history": "Clinical History",
    "blood_group": "Blood Group",
    "transfusion_history": "Transfusion History",
    "sample_id": "Sample ID",
    "blood_require_date": "Blood Require Date",
    "request_type": "Reason of Request",
    "sample_date": "Received Sample Date",
    "mother_name": "Mother's Name",
    "diagnosis": "Diagnosis",
    "relation": "Relation",
    "is_aliqout": "Is Aliquot",
    "aliqout_method": "Aliquot Method",
    "transfusion_reason": "Transfusion Reason",
    "thalassemia_id": "Thalassemia ID",
    "searchfor": "Search For",
    "attendee_name": "Attendee Name",
    "attendee_relation": "Attendee Relation",
    "attendee_mobile": "Attendee Mobile",
    "ward_number": "Ward Number",
    "bed_number": "Bed Number",
    "cross_match_for": "Cross Match For",
    "component_details": "Component Details",
}
