#!/usr/bin/env python3
"""Generate PDF report for Al Sinama ROLAP Data Warehouse schema."""

import subprocess
from fpdf import FPDF

class Report(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "Al Sinama Data Warehouse - ROLAP Schema Report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_fill_color(230, 230, 250)
        self.cell(0, 9, title, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(40, 40, 120)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 9)
        self.multi_cell(0, 5, text)
        self.ln(1)

    def attr_table(self, rows):
        """rows: list of (attribute, type, description)"""
        self.set_font("Helvetica", "B", 8)
        col_w = [38, 32, 120]
        headers = ["Attribute", "Type", "Description"]
        self.set_fill_color(200, 200, 220)
        for i, h in enumerate(headers):
            self.cell(col_w[i], 6, h, border=1, fill=True)
        self.ln()
        self.set_font("Helvetica", "", 7.5)
        for attr, typ, desc in rows:
            max_lines = max(1, len(desc) // 45 + 1)
            h = 5 * max_lines
            x0, y0 = self.get_x(), self.get_y()
            if y0 + h > 270:
                self.add_page()
                x0, y0 = self.get_x(), self.get_y()
            self.multi_cell(col_w[0], 5, attr, border=1)
            y1 = self.get_y()
            self.set_xy(x0 + col_w[0], y0)
            self.multi_cell(col_w[1], 5, typ, border=1)
            y2 = self.get_y()
            self.set_xy(x0 + col_w[0] + col_w[1], y0)
            self.multi_cell(col_w[2], 5, desc, border=1)
            y3 = self.get_y()
            self.set_y(max(y1, y2, y3))
        self.ln(2)

    def pg_screenshot(self, title, output):
        """Render psql output as monospace text block."""
        self.sub_title(f"PostgreSQL Output: {title}")
        self.set_font("Courier", "", 6.5)
        self.set_fill_color(245, 245, 245)
        for line in output.strip().split("\n"):
            if self.get_y() > 272:
                self.add_page()
            self.cell(0, 3.5, line[:140], fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)


def get_psql_output(sql):
    """Run SQL via docker and return output."""
    result = subprocess.run(
        ["docker", "exec", "as_datawarehouse", "psql", "-U", "admin", "-d", "as_warehouse", "-c", sql],
        capture_output=True, text=True
    )
    return result.stdout


def main():
    pdf = Report()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.alias_nb_pages()
    pdf.add_page()

    # ---- Title Page ----
    pdf.set_font("Helvetica", "B", 22)
    pdf.ln(30)
    pdf.cell(0, 12, "Al Sinama (AS)", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Data Warehouse ROLAP Schema Design", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "Database Management - Spring 2026", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "HBKU", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "Ali Al-Saifi", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "ID: 210089822", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6,
        "This report presents the ROLAP (Relational Online Analytical Processing) star schema "
        "designed for the Al Sinama cinema operator's data warehouse. The schema is based on the "
        "operational ER diagram and is optimized to support the ten target analytical queries "
        "involving ticket sales analysis across multiple dimensions."
    )

    # ---- Assumptions ----
    pdf.add_page()
    pdf.section_title("1. Design Assumptions")
    assumptions = [
        "1. The grain of the fact table is one transaction. Each transaction is associated with exactly one customer, one showing (and therefore one movie, one hall, one cinema), and optionally one promotion.",
        "2. Hall size categories are defined as: Small (capacity <= 50 seats), Mid-size (51-150 seats), Large (> 150 seats).",
        "3. Time of day for showings is categorized as: Morning (before 12:00), Afternoon (12:00-17:59), Night (18:00 and later).",
        "4. Age groups for customer analysis: [0-10], [11-20], [21-30], [31-40], [41-50], [51-60], [61+]. Age is computed at query time from customer date of birth and transaction date.",
        "5. 'State' is extracted from the Cinema address field as a separate attribute in the cinema dimension.",
        "6. Transactions without a promotion are linked to a special 'No Promotion' row (promotion_key = 0) in the promotion dimension.",
        "7. The online/offline channel type is modeled as a separate dimension (dim_channel) derived from the OnlineTrans/OfflineTrans ISA hierarchy.",
        "8. Movie-to-Star and Movie-to-Director are many-to-many relationships, modeled via bridge tables.",
        "9. ticket_count (number of tickets per transaction) is stored as a measure in the fact table to support Query 5.",
        "10. Two date foreign keys exist in the fact table: date_key (transaction date) and showing_date_key (showing date), as these may differ.",
    ]
    for a in assumptions:
        pdf.body_text(a)

    # ---- Schema Overview ----
    pdf.add_page()
    pdf.section_title("2. Star Schema Overview")
    pdf.body_text(
        "The ROLAP schema follows a star schema design with one central fact table (fact_sales) "
        "surrounded by eight dimension tables and two bridge tables. The schema is summarized below:"
    )
    pdf.body_text(
        "Fact Table: fact_sales\n"
        "Dimension Tables: dim_date, dim_time, dim_customer, dim_movie, dim_cinema, dim_hall, dim_promotion, dim_channel\n"
        "Bridge Tables: bridge_movie_director, bridge_movie_star"
    )
    pdf.body_text(
        "The star schema connects to each dimension via surrogate integer keys. "
        "The fact table stores two measures: total_price (the monetary value of the transaction) "
        "and ticket_count (the number of tickets purchased in the transaction). "
        "The transaction_id serves as a degenerate dimension."
    )

    # ---- Detailed Table Descriptions ----
    pdf.add_page()
    pdf.section_title("3. Table Definitions and Attribute Descriptions")

    # -- dim_date --
    pdf.sub_title("3.1  dim_date (Date Dimension)")
    pdf.body_text("Derived from Transaction.Date and Showing.Date. Supports analysis by year, month, quarter, and weekday/weekend. Used in Queries 1, 2, 3, 4, 5, 7, 9, 10.")
    pdf.attr_table([
        ("date_key", "INT (PK)", "Surrogate primary key in YYYYMMDD format (e.g., 20180115)."),
        ("full_date", "DATE", "The actual calendar date."),
        ("day_of_week", "VARCHAR(10)", "Name of the day (e.g., 'Monday', 'Saturday')."),
        ("is_weekend", "BOOLEAN", "TRUE if the date falls on Saturday or Sunday; FALSE otherwise. Supports Query 3 (weekday vs weekend)."),
        ("day_of_month", "INT", "Day number within the month (1-31)."),
        ("month", "INT", "Month number (1-12). Supports Query 2 (monthly ROLLUP)."),
        ("month_name", "VARCHAR(10)", "Full month name (e.g., 'January')."),
        ("quarter", "INT", "Calendar quarter (1-4)."),
        ("year", "INT", "Calendar year (e.g., 2018). Supports Queries 1, 2, 7, 10."),
    ])

    # -- dim_time --
    pdf.sub_title("3.2  dim_time (Time-of-Day Dimension)")
    pdf.body_text("Derived from Showing.Time. Categorizes showings into morning, afternoon, or night. Used in Query 6.")
    pdf.attr_table([
        ("time_key", "INT (PK)", "Surrogate primary key."),
        ("full_time", "TIME", "The actual showing time."),
        ("hour", "INT", "Hour component (0-23)."),
        ("time_of_day", "VARCHAR(10)", "Category: 'Morning' (< 12:00), 'Afternoon' (12:00-17:59), or 'Night' (>= 18:00). Supports Query 6."),
    ])

    # -- dim_customer --
    pdf.sub_title("3.3  dim_customer (Customer Dimension)")
    pdf.body_text("Derived from the Customer entity. Supports analysis by gender and age. Used in Queries 1, 4, 5, 6, 8, 10.")
    pdf.attr_table([
        ("customer_key", "INT (PK)", "Surrogate primary key."),
        ("customer_id", "INT", "Original Customer.ID from the operational database."),
        ("name", "VARCHAR(100)", "Customer's full name."),
        ("gender", "VARCHAR(10)", "Customer's gender ('Male' or 'Female'). Supports Queries 1, 4, 5, 6, 8, 10."),
        ("date_of_birth", "DATE", "Customer's date of birth. Used to compute age at time of purchase for Query 10."),
        ("address", "VARCHAR(200)", "Customer's address."),
    ])

    # -- dim_movie --
    pdf.sub_title("3.4  dim_movie (Movie Dimension)")
    pdf.body_text("Derived from the Movie entity. Supports analysis by genre. Used in Queries 3, 7, 8.")
    pdf.attr_table([
        ("movie_key", "INT (PK)", "Surrogate primary key."),
        ("movie_id", "INT", "Original Movie.ID from the operational database."),
        ("title", "VARCHAR(200)", "Title of the movie."),
        ("genre", "VARCHAR(50)", "Genre of the movie (e.g., 'Drama', 'Comedy'). Supports Queries 3, 8."),
        ("release_date", "DATE", "Date the movie was released."),
        ("language", "VARCHAR(50)", "Language of the movie."),
        ("cost", "NUMERIC(12,2)", "Production cost of the movie."),
        ("country", "VARCHAR(50)", "Country of origin."),
    ])

    # -- bridge_movie_director --
    pdf.sub_title("3.5  bridge_movie_director (Movie-Director Bridge)")
    pdf.body_text("Bridge table linking movies to their directors (many-to-many). Supports Query 7 (filtering by director name).")
    pdf.attr_table([
        ("movie_key", "INT (PK, FK)", "Foreign key to dim_movie. Part of composite primary key."),
        ("director_id", "INT (PK)", "Original Director.ID. Part of composite primary key."),
        ("director_name", "VARCHAR(100)", "Director's name, denormalized for efficient querying (e.g., 'Mohamed Khan' in Query 7)."),
    ])

    # -- bridge_movie_star --
    pdf.sub_title("3.6  bridge_movie_star (Movie-Star Bridge)")
    pdf.body_text("Bridge table linking movies to their cast/stars (many-to-many). Supports Query 8 (filtering by star name).")
    pdf.attr_table([
        ("movie_key", "INT (PK, FK)", "Foreign key to dim_movie. Part of composite primary key."),
        ("star_id", "INT (PK)", "Original Star.ID. Part of composite primary key."),
        ("star_name", "VARCHAR(100)", "Star's name, denormalized for efficient querying (e.g., 'Omar Sharif' in Query 8)."),
    ])

    # -- dim_cinema --
    pdf.sub_title("3.7  dim_cinema (Cinema Dimension)")
    pdf.body_text("Derived from the Cinema entity. Supports analysis by state/location. Used in Queries 7, 9.")
    pdf.attr_table([
        ("cinema_key", "INT (PK)", "Surrogate primary key."),
        ("cinema_id", "INT", "Original Cinema.ID from the operational database."),
        ("cinema_name", "VARCHAR(100)", "Name of the cinema."),
        ("address", "VARCHAR(200)", "Full address of the cinema."),
        ("state", "VARCHAR(50)", "State extracted from the cinema address. Supports Queries 7, 9."),
    ])

    # -- dim_hall --
    pdf.sub_title("3.8  dim_hall (Hall Dimension)")
    pdf.body_text("Derived from the Hall entity. Supports analysis by hall size category. Used in Query 9.")
    pdf.attr_table([
        ("hall_key", "INT (PK)", "Surrogate primary key."),
        ("hall_id", "INT", "Original Hall.ID from the operational database."),
        ("size", "INT", "Number of seats in the hall."),
        ("size_category", "VARCHAR(10)", "Categorization: 'Small' (<= 50 seats), 'Mid' (51-150 seats), 'Large' (> 150 seats). Supports Query 9."),
        ("price", "NUMERIC(8,2)", "Base ticket price for this hall."),
    ])

    # -- dim_promotion --
    pdf.sub_title("3.9  dim_promotion (Promotion Dimension)")
    pdf.body_text("Derived from the Promotion entity. Includes a default 'No Promotion' row (key=0) for transactions without promotions. Used in Query 4.")
    pdf.attr_table([
        ("promotion_key", "INT (PK)", "Surrogate primary key. 0 = No Promotion."),
        ("promotion_id", "INT", "Original Promotion.ID (NULL for the 'No Promotion' row)."),
        ("description", "VARCHAR(200)", "Promotion type/description. Supports Query 4."),
        ("discount", "NUMERIC(5,2)", "Discount value (percentage or fixed amount)."),
        ("start_date", "DATE", "Start date of the promotion period."),
        ("end_date", "DATE", "End date of the promotion period."),
    ])

    # -- dim_channel --
    pdf.sub_title("3.10  dim_channel (Channel Dimension)")
    pdf.body_text("Derived from the OnlineTrans/OfflineTrans ISA subtype of Transaction. Supports analysis by online vs offline. Used in Queries 2, 9.")
    pdf.attr_table([
        ("channel_key", "INT (PK)", "Surrogate primary key."),
        ("channel_type", "VARCHAR(10)", "'Online' or 'Offline'. Supports Queries 2, 9."),
        ("system", "VARCHAR(50)", "Operating system used for online transactions (NULL if offline)."),
        ("browser", "VARCHAR(50)", "Browser used for online transactions (NULL if offline)."),
    ])

    # -- fact_sales --
    pdf.add_page()
    pdf.sub_title("3.11  fact_sales (Fact Table)")
    pdf.body_text(
        "Central fact table at the grain of one transaction. Each row represents a single ticket purchase transaction. "
        "Contains foreign keys to all dimension tables and two additive measures."
    )
    pdf.attr_table([
        ("transaction_id", "INT (PK)", "Degenerate dimension. Original Transaction.ID from the operational database."),
        ("date_key", "INT (FK)", "Foreign key to dim_date. Date when the transaction occurred."),
        ("showing_date_key", "INT (FK)", "Foreign key to dim_date. Date of the movie showing. Supports Query 3 (weekday/weekend of showing)."),
        ("time_key", "INT (FK)", "Foreign key to dim_time. Time of the movie showing. Supports Query 6 (morning/afternoon/night)."),
        ("customer_key", "INT (FK)", "Foreign key to dim_customer. The customer who made the purchase."),
        ("movie_key", "INT (FK)", "Foreign key to dim_movie. The movie being shown."),
        ("cinema_key", "INT (FK)", "Foreign key to dim_cinema. The cinema where the showing takes place."),
        ("hall_key", "INT (FK)", "Foreign key to dim_hall. The hall within the cinema."),
        ("promotion_key", "INT (FK)", "Foreign key to dim_promotion. Promotion applied (0 = none). Supports Query 4."),
        ("channel_key", "INT (FK)", "Foreign key to dim_channel. Online or offline purchase channel. Supports Queries 2, 9."),
        ("total_price", "NUMERIC(10,2)", "MEASURE: Total monetary amount of the transaction (Transaction.TotalPrice). Primary measure for all 'total sales' queries."),
        ("ticket_count", "INT", "MEASURE: Number of tickets purchased in this transaction. Supports Queries 5 and 6."),
    ])

    # ---- Query-to-Table Mapping ----
    pdf.add_page()
    pdf.section_title("4. Query-to-Schema Mapping")
    pdf.body_text("The following table shows which dimensions and measures each target query uses:")
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_fill_color(200, 200, 220)
    qcols = [12, 85, 93]
    for i, h in enumerate(["Query", "Dimensions Used", "Measures / Notes"]):
        pdf.cell(qcols[i], 6, h, border=1, fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 7)
    queries = [
        ("Q1", "dim_date (year), dim_customer (gender)", "SUM(total_price)"),
        ("Q2", "dim_date (month ROLLUP year), dim_channel (online/offline)", "SUM(total_price)"),
        ("Q3", "dim_movie (genre), dim_date via showing_date_key (weekday/weekend)", "SUM(total_price)"),
        ("Q4", "dim_customer (gender), dim_promotion (description), dim_date (year=2018)", "SUM(total_price)"),
        ("Q5", "dim_customer (gender), fact_sales (ticket_count), dim_date (year=2018)", "SUM(total_price)"),
        ("Q6", "dim_customer (gender), dim_time (time_of_day), dim_date (year=2018)", "SUM(ticket_count)"),
        ("Q7", "dim_date (year 2015-2018), dim_cinema (state), bridge_movie_director (name filter)", "SUM(total_price)"),
        ("Q8", "dim_movie (genre), dim_customer (gender), bridge_movie_star (name filter)", "SUM(total_price)"),
        ("Q9", "dim_cinema (state), dim_hall (size_category), dim_channel (offline), dim_date (2018)", "SUM(total_price)"),
        ("Q10", "dim_customer (gender, DOB->age->age group), dim_date (year 2015-2018)", "SUM(total_price)"),
    ]
    for q, dims, meas in queries:
        x0, y0 = pdf.get_x(), pdf.get_y()
        if y0 > 265:
            pdf.add_page()
            x0, y0 = pdf.get_x(), pdf.get_y()
        pdf.multi_cell(qcols[0], 5, q, border=1)
        y1 = pdf.get_y()
        pdf.set_xy(x0 + qcols[0], y0)
        pdf.multi_cell(qcols[1], 5, dims, border=1)
        y2 = pdf.get_y()
        pdf.set_xy(x0 + qcols[0] + qcols[1], y0)
        pdf.multi_cell(qcols[2], 5, meas, border=1)
        y3 = pdf.get_y()
        pdf.set_y(max(y1, y2, y3))

    # ---- PostgreSQL Screenshots ----
    pdf.add_page()
    pdf.section_title("5. PostgreSQL Table Screenshots")
    pdf.body_text("The following sections show the actual PostgreSQL table structures as created in the database (PostgreSQL 16, running in Docker).")

    tables = [
        ("dim_date", "\\d dim_date"),
        ("dim_time", "\\d dim_time"),
        ("dim_customer", "\\d dim_customer"),
        ("dim_movie", "\\d dim_movie"),
        ("bridge_movie_director", "\\d bridge_movie_director"),
        ("bridge_movie_star", "\\d bridge_movie_star"),
        ("dim_cinema", "\\d dim_cinema"),
        ("dim_hall", "\\d dim_hall"),
        ("dim_promotion", "\\d dim_promotion"),
        ("dim_channel", "\\d dim_channel"),
        ("fact_sales", "\\d fact_sales"),
    ]

    for tname, cmd in tables:
        output = get_psql_output(cmd)
        pdf.pg_screenshot(tname, output)

    # All tables listing
    output = get_psql_output("\\dt")
    pdf.pg_screenshot("All Tables (\\dt)", output)

    # Foreign keys
    fk_sql = """
    SELECT tc.constraint_name, kcu.column_name,
           ccu.table_name AS references_table, ccu.column_name AS references_column
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
    WHERE tc.table_name = 'fact_sales' AND tc.constraint_type = 'FOREIGN KEY'
    ORDER BY kcu.column_name;
    """
    output = get_psql_output(fk_sql)
    pdf.pg_screenshot("fact_sales Foreign Key Relationships", output)

    # dim_promotion data
    output = get_psql_output("SELECT * FROM dim_promotion;")
    pdf.pg_screenshot("dim_promotion Data (default 'No Promotion' row)", output)

    # ---- Save ----
    outpath = "/Users/ali.alsaifi/Library/CloudStorage/OneDrive-applab.qa/HBKU/Spring-2026/Database-Management/project1/ROLAP_Schema_Report.pdf"
    pdf.output(outpath)
    print(f"Report saved to: {outpath}")


if __name__ == "__main__":
    main()
