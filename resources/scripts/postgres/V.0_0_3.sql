-- Add user_id column to doctors table
ALTER TABLE appointment_mgmt.doctors
ADD COLUMN IF NOT EXISTS user_id INTEGER UNIQUE;

-- Add user_id column to patients table
ALTER TABLE appointment_mgmt.patients
ADD COLUMN IF NOT EXISTS user_id INTEGER UNIQUE;

-- Add updated_at column to doctors table
ALTER TABLE appointment_mgmt.doctors
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL;

-- Add updated_at column to patients table
ALTER TABLE appointment_mgmt.patients
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL;

-- Create indexes for user_id lookups
CREATE INDEX IF NOT EXISTS idx_doctors_user_id ON appointment_mgmt.doctors(user_id);
CREATE INDEX IF NOT EXISTS idx_patients_user_id ON appointment_mgmt.patients(user_id);

-- Insert departments
INSERT INTO appointment_mgmt.departments (name) VALUES
('Khoa Tim mạch'),
('Khoa Thần kinh'),
('Khoa Da liễu'),
('Khoa Tai mũi họng');

-- Insert doctors
INSERT INTO appointment_mgmt.doctors (name, department_id, user_id) VALUES
('BS. Nguyễn Văn A', 1, 2),
('BS. Trần Thị B', 1, 1),
('BS. Lê Văn C', 2, 3),
('BS. Phạm Thị D', 3, 4);

-- Insert doctors
INSERT INTO appointment_mgmt.patients (name,phone, email, user_id) VALUES
('Trần Văn F', 11231231, 'f.van@gmail.com',5),
('Bùi Công A', 1312312,'a.bui@gmail.com',6),
('Nguyễn Ngọc K', 2123123,'k.nguyen@gmail.com',7),
('Lê Văn S', 322233,'s.le@gmail.com',8);

-- Insert available slots (example)
INSERT INTO appointment_mgmt.doctor_available_slots (doctor_id, available_date, start_time, end_time) VALUES
(1, CURRENT_DATE + 1, '08:00', '08:30'),
(1, CURRENT_DATE + 1, '08:30', '09:00'),
(1, CURRENT_DATE + 1, '09:00', '09:30'),
(2, CURRENT_DATE + 1, '14:00', '14:30'),
(2, CURRENT_DATE + 1, '14:30', '15:00'),
(3, CURRENT_DATE + 2, '10:00', '10:30'),
(3, CURRENT_DATE + 2, '10:30', '11:00');
