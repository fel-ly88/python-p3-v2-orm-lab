from __init__ import CURSOR, CONN
from department import Department
from employee import Employee




class Review:
    all = {}  # cache of Review instances

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return f"<Review id={self.id}, year={self.year}, summary={self.summary}, employee_id={self.employee_id}>"

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INTEGER,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CONN.commit()
        
        
    def save(self):
        if self.id is None:
            CURSOR.execute(
                "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)",
                (self.year, self.summary, self.employee_id)
            )
            CONN.commit()
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
        else:
            self.update()


    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

   
    @classmethod
    def instance_from_db(cls, row):
        if row[0] in cls.all:
            return cls.all[row[0]]
        review = cls(row[1], row[2], row[3], id=row[0])
        cls.all[row[0]] = review
        return review

   
    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute("SELECT * FROM reviews WHERE id=?", (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        CURSOR.execute(
            "UPDATE reviews SET year=?, summary=?, employee_id=? WHERE id=?",
            (self.year, self.summary, self.employee_id, self.id)
        )
        CONN.commit()

    def delete(self):
        if self.id:
            CURSOR.execute("DELETE FROM reviews WHERE id=?", (self.id,))
            CONN.commit()
            Review.all.pop(self.id, None)
            self.id = None
    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM reviews")
        return [cls.instance_from_db(row) for row in CURSOR.fetchall()]



    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise ValueError("Year must be an integer")
        if value < 2000:
            raise ValueError("Year must be >= 2000")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str):
            raise ValueError("Summary must be a string")
        if len(value.strip()) == 0:
            raise ValueError("Summary cannot be empty")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        CURSOR.execute("SELECT id FROM employees WHERE id = ?", (value,))
        if not CURSOR.fetchone():
            raise ValueError("Employee ID must exist in employees table")
        self._employee_id = value

    @classmethod
    def instance_from_db(cls, row):
        return cls(row[1], row[2], row[3], id=row[0])
    
    def reviews(self):
        """Return all Review instances for this Employee"""
        from review import Review   # local import avoids circular dependency

        sql = "SELECT * FROM reviews WHERE employee_id = ?"
        rows = CURSOR.execute(sql, (self.id,)).fetchall()
        return [Review.instance_from_db(row) for row in rows]
