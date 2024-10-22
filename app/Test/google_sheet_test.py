from app.Services.google_sheet import GoogleSheet

google_sheet = GoogleSheet()

res = google_sheet.create_data('CLASS_2', 1, 'Nguyen Van A')
print(res)
res = google_sheet.create_data('CLASS_2', 2, 'Nguyen Van B')
print(res)

res = google_sheet.push('CLASS_2', 1)
print(res)
res = google_sheet.push('CLASS_2', 2)
print(res)
