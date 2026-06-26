CREATE TABLE IF NOT EXISTS students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    major VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO students (name, age, major, created_at) VALUES
    ('Alice Zhang', 20, 'Computer Science', '2026-06-01 09:00:00'),
    ('Bob Li', 21, 'Mathematics', '2026-06-02 09:30:00'),
    ('Carol Wang', 19, 'Physics', '2026-06-03 10:00:00'),
    ('David Chen', 22, 'Economics', '2026-06-04 10:30:00'),
    ('Eve Liu', 20, 'Data Science', '2026-06-05 11:00:00');
