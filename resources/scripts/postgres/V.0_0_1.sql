CREATE SCHEMA IF NOT EXISTS appointment_mgmt;

CREATE TYPE appointment_mgmt.appointment_status AS ENUM (
'PENDING',          -- Chờ xác nhận
'CONFIRMED',        -- Đã xác nhận
'REJECTED',         -- Đã từ chối
'CANCELLED'         -- Đã hủy
);


CREATE TABLE IF NOT EXISTS appointment_mgmt.departments (
id SERIAL PRIMARY KEY,
name VARCHAR(100) NOT NULL,
is_active BOOLEAN DEFAULT TRUE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);


CREATE TABLE IF NOT EXISTS appointment_mgmt.doctors (
id SERIAL PRIMARY KEY,
name VARCHAR(100) NOT NULL,
department_id INTEGER NOT NULL REFERENCES appointment_mgmt.departments(id),
is_active BOOLEAN DEFAULT TRUE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);


CREATE TABLE IF NOT EXISTS appointment_mgmt.doctor_available_slots (
id SERIAL PRIMARY KEY,
doctor_id INTEGER NOT NULL REFERENCES appointment_mgmt.doctors(id) ON DELETE CASCADE,
available_date DATE NOT NULL,
start_time TIME NOT NULL,
end_time TIME NOT NULL,
is_booked BOOLEAN DEFAULT FALSE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

CONSTRAINT unique_doctor_slot UNIQUE (doctor_id, available_date, start_time)
);


CREATE TABLE IF NOT EXISTS appointment_mgmt.patients (
id SERIAL PRIMARY KEY,
name VARCHAR(100) NOT NULL,
phone VARCHAR(20),
email VARCHAR(100),
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);


CREATE TABLE IF NOT EXISTS appointment_mgmt.appointments (
id SERIAL PRIMARY KEY,


patient_id INTEGER NOT NULL REFERENCES appointment_mgmt.patients(id),
doctor_id INTEGER NOT NULL REFERENCES appointment_mgmt.doctors(id),
department_id INTEGER NOT NULL REFERENCES appointment_mgmt.departments(id),
slot_id INTEGER NOT NULL REFERENCES appointment_mgmt.doctor_available_slots(id),


appointment_date DATE NOT NULL,
appointment_time TIME NOT NULL,
reason TEXT NOT NULL, -- Lý do khám (use case: bệnh nhân nhập lý do)
is_emergency BOOLEAN DEFAULT FALSE NOT NULL, -- Emergency appointment flag

-- Trạng thái và xử lý
status appointment_mgmt.appointment_status DEFAULT 'PENDING',

-- Use case: Xác nhận lịch khám
confirmed_by INTEGER REFERENCES appointment_mgmt.doctors(id),
confirmed_at TIMESTAMP,

-- Use case: Từ chối lịch khám
rejection_reason TEXT,
rejected_at TIMESTAMP,

-- Use case: Hủy lịch khám
cancelled_by VARCHAR(20), -- 'PATIENT' hoặc 'DOCTOR'
cancelled_at TIMESTAMP,
cancellation_reason TEXT,

-- Audit
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

-- Constraints theo use cases
CONSTRAINT valid_confirmation CHECK (
(status = 'CONFIRMED' AND confirmed_by IS NOT NULL AND confirmed_at IS NOT NULL) OR
(status != 'CONFIRMED')
),
CONSTRAINT valid_rejection CHECK (
(status = 'REJECTED' AND rejection_reason IS NOT NULL AND rejected_at IS NOT NULL) OR
(status != 'REJECTED')
),
CONSTRAINT valid_cancellation CHECK (
(status = 'CANCELLED' AND cancelled_by IS NOT NULL AND cancelled_at IS NOT NULL) OR
(status != 'CANCELLED')
)
);

-- =============================================
-- INDEXES for Use Cases Performance
-- =============================================

-- Use case: Lấy danh sách khoa
CREATE INDEX idx_departments_active ON appointment_mgmt.departments(is_active);

-- Use case: Lấy bác sĩ theo khoa
CREATE INDEX idx_doctors_department ON appointment_mgmt.doctors(department_id, is_active);

-- Use case: Tìm lịch trống của bác sĩ
CREATE INDEX idx_available_slots_doctor_date ON appointment_mgmt.doctor_available_slots(doctor_id, available_date, is_booked);

-- Use case: Quản lý lịch khám
CREATE INDEX idx_appointments_patient ON appointment_mgmt.appointments(patient_id);
CREATE INDEX idx_appointments_doctor ON appointment_mgmt.appointments(doctor_id);
CREATE INDEX idx_appointments_status ON appointment_mgmt.appointments(status);
CREATE INDEX idx_appointments_date ON appointment_mgmt.appointments(appointment_date);
CREATE INDEX idx_appointments_emergency ON appointment_mgmt.appointments(is_emergency, status);
CREATE INDEX idx_appointments_emergency_date ON appointment_mgmt.appointments(is_emergency, appointment_date);

-- Use case: Lấy lịch chờ xác nhận
CREATE INDEX idx_appointments_pending ON appointment_mgmt.appointments(doctor_id, status)
WHERE status = 'PENDING';

-- =============================================
-- TRIGGERS
-- =============================================

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION appointment_mgmt.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
NEW.updated_at = CURRENT_TIMESTAMP;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER appointments_updated_at
BEFORE UPDATE ON appointment_mgmt.appointments
FOR EACH ROW EXECUTE FUNCTION appointment_mgmt.update_updated_at();

-- Auto-book slot when appointment created (Use case: Đặt lịch khám)
CREATE OR REPLACE FUNCTION appointment_mgmt.book_slot()
RETURNS TRIGGER AS $$
BEGIN
-- Mark slot as booked
UPDATE appointment_mgmt.doctor_available_slots
SET is_booked = TRUE
WHERE id = NEW.slot_id;

RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER book_slot_trigger
AFTER INSERT ON appointment_mgmt.appointments
FOR EACH ROW EXECUTE FUNCTION appointment_mgmt.book_slot();

-- Auto-release slot when appointment cancelled (Use case: Hủy lịch khám)
CREATE OR REPLACE FUNCTION appointment_mgmt.release_slot()
RETURNS TRIGGER AS $$
BEGIN
-- Release slot if cancelled
IF NEW.status = 'CANCELLED' AND OLD.status != 'CANCELLED' THEN
UPDATE appointment_mgmt.doctor_available_slots
SET is_booked = FALSE
WHERE id = NEW.slot_id;
END IF;

RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER release_slot_trigger
AFTER UPDATE ON appointment_mgmt.appointments
FOR EACH ROW EXECUTE FUNCTION appointment_mgmt.release_slot();

-- =============================================
-- VIEWS for Use Cases
-- =============================================

-- View: Danh sách lịch khám của bệnh nhân (Use case: Cập nhật, Hủy lịch)
CREATE OR REPLACE VIEW appointment_mgmt.v_patient_appointments AS
SELECT
a.id,
a.patient_id,
p.name as patient_name,
d.name as doctor_name,
dept.name as department_name,
a.appointment_date,
a.appointment_time,
a.reason,
a.is_emergency,
a.status,
a.created_at
FROM appointment_mgmt.appointments a
JOIN appointment_mgmt.patients p ON a.patient_id = p.id
JOIN appointment_mgmt.doctors d ON a.doctor_id = d.id
JOIN appointment_mgmt.departments dept ON a.department_id = dept.id;

-- View: Lịch chờ xác nhận của bác sĩ (Use case: Xác nhận lịch khám)
CREATE OR REPLACE VIEW appointment_mgmt.v_pending_appointments AS
SELECT
a.id,
a.doctor_id,
p.name as patient_name,
p.phone as patient_phone,
d.name as doctor_name,
dept.name as department_name,
a.appointment_date,
a.appointment_time,
a.reason,
a.is_emergency,
a.created_at
FROM appointment_mgmt.appointments a
JOIN appointment_mgmt.patients p ON a.patient_id = p.id
JOIN appointment_mgmt.doctors d ON a.doctor_id = d.id
JOIN appointment_mgmt.departments dept ON a.department_id = dept.id
WHERE a.status = 'PENDING'
ORDER BY a.is_emergency DESC, a.created_at ASC;

-- View: Lịch trống của bác sĩ (Use case: Đặt lịch khám)
CREATE OR REPLACE VIEW appointment_mgmt.v_available_slots AS
SELECT
s.id as slot_id,
s.doctor_id,
d.name as doctor_name,
dept.name as department_name,
s.available_date,
s.start_time,
s.end_time
FROM appointment_mgmt.doctor_available_slots s
JOIN appointment_mgmt.doctors d ON s.doctor_id = d.id
JOIN appointment_mgmt.departments dept ON d.department_id = dept.id
WHERE s.is_booked = FALSE
AND s.available_date >= CURRENT_DATE
AND d.is_active = TRUE;


-- Insert departments
INSERT INTO appointment_mgmt.departments (name) VALUES
('Khoa Tim mạch'),
('Khoa Thần kinh'),
('Khoa Da liễu'),
('Khoa Tai mũi họng');

-- Insert doctors
INSERT INTO appointment_mgmt.doctors (name, department_id) VALUES
('BS. Nguyễn Văn A', 1),
('BS. Trần Thị B', 1),
('BS. Lê Văn C', 2),
('BS. Phạm Thị D', 3);

-- Insert available slots (example)
INSERT INTO appointment_mgmt.doctor_available_slots (doctor_id, available_date, start_time, end_time) VALUES
(1, CURRENT_DATE + 1, '08:00', '08:30'),
(1, CURRENT_DATE + 1, '08:30', '09:00'),
(1, CURRENT_DATE + 1, '09:00', '09:30'),
(2, CURRENT_DATE + 1, '14:00', '14:30'),
(2, CURRENT_DATE + 1, '14:30', '15:00'),
(3, CURRENT_DATE + 2, '10:00', '10:30'),
(3, CURRENT_DATE + 2, '10:30', '11:00');

