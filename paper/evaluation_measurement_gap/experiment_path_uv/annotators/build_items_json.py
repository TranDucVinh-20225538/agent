import csv, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
VI = {
"Browse recipes for gluten-free chocolate chip cookies that can be made without nuts.": "Tìm công thức bánh quy chocolate chip không gluten và không có hạt (nut).",
"Calculate the shipping cost for 4 pound package from Texas to New York.": "Tính chi phí vận chuyển cho kiện hàng 4 pound từ Texas đến New York.",
"Check if a visa is required to work in the UK for longer than 6 months in Healthcare as an American citizen.": "Kiểm tra xem công dân Mỹ có cần visa để làm việc trong ngành y tế tại Anh hơn 6 tháng không.",
"Check the status of bus S92 for any disruptions on new.mta.info.": "Kiểm tra tình trạng tuyến xe buýt S92 xem có gián đoạn gì không trên new.mta.info.",
"Complete a multiplication quiz on https://www.coolmath4kids.com/, covering multiplication facts for 11-12. The quiz should consist of 10 questions, with unlimited time allowed for each. The goal is to achieve a perfect score of 10 out of 10.": "Hoàn thành bài quiz nhân bảng cửu chương 11-12 trên coolmath4kids.com, gồm 10 câu, không giới hạn thời gian, mục tiêu đạt điểm tuyệt đối 10/10.",
"Estimate the federal income tax I would owe on $158,500 of taxable income in ZIP code 97007, filing as single.": "Ước tính thuế thu nhập liên bang phải đóng với thu nhập chịu thuế $158,500 tại mã zip 97007, khai độc thân.",
"Find 12 Monkeys community and view the latest posts mentioning James Cole.": "Tìm cộng đồng '12 Monkeys' và xem các bài đăng mới nhất có nhắc tới James Cole.",
"Find a 2022 Tesla Model 3 on CarMax.": "Tìm xe Tesla Model 3 đời 2022 trên CarMax.",
"Find a female MD Cardiologist in Jacksonville, Florida.": "Tìm bác sĩ tim mạch (MD) nữ tại Jacksonville, Florida.",
"Find a gas station in Manhattan, NY with a rating above 4.0, and sort the user reviews by the lowest rating.": "Tìm trạm xăng ở Manhattan, NY có đánh giá trên 4.0, sắp xếp review theo đánh giá thấp nhất.",
"Find a house cleaning service in 10001 on a weekly basis.": "Tìm dịch vụ dọn nhà theo tuần ở khu vực mã zip 10001.",
"Find a neurosurgeon who is over 50 years old and has an appointment available tomorrow.": "Tìm bác sĩ phẫu thuật thần kinh trên 50 tuổi, có lịch hẹn trống vào ngày mai.",
"Find an Airbnb in Cleveland for three nights. The check-in date is the day after tomorrow. We have 2 adults, 2 kids, and 1 pet. The budget is $100 to $300 per night. Essential amenities include free parking, a washer, and a gym.": "Tìm Airbnb ở Cleveland cho 3 đêm, nhận phòng ngày kia, 2 người lớn + 2 trẻ em + 1 thú cưng, ngân sách $100–300/đêm, cần có bãi đỗ xe miễn phí, máy giặt và phòng gym.",
"Find an energetic hairless dog with medium barking.": "Tìm một chú chó không lông, năng động, mức độ sủa trung bình.",
"Find parking near the San Francisco Museum of Modern Art from June 18, 1:00 PM to 5:00 PM. I'm driving a Ford F-150 and need a garage that allows in-and-out privileges. If there are multiple options, show me the details of the one with the lowest price.": "Tìm chỗ đỗ xe gần Bảo tàng Nghệ thuật Hiện đại San Francisco từ 13h–17h ngày 18/6, lái xe Ford F-150, cần bãi cho ra vào nhiều lần; nếu có nhiều lựa chọn thì lấy chỗ rẻ nhất.",
"Find press releases by the antitrust division in 2022.": "Tìm các thông cáo báo chí của bộ phận chống độc quyền (antitrust) năm 2022.",
"Find the 5-day price chart for Bitcoin.": "Tìm biểu đồ giá Bitcoin trong 5 ngày gần nhất.",
"Find the Eligibility to get the child benefit and How it works and how to claim": "Tìm điều kiện được hưởng trợ cấp trẻ em, cách thức hoạt động và cách đăng ký nhận.",
"Find the HGX H100 driver for Ubuntu 22.04 on AMD64 CPU.": "Tìm driver cho HGX H100 trên Ubuntu 22.04, kiến trúc AMD64.",
"Find the app for iOS.": "Tìm ứng dụng dành cho iOS.",
"Find the best-selling vinyl record by an artist from New York City in the classical music genre.": "Tìm đĩa vinyl bán chạy nhất của một nghệ sĩ đến từ New York City, thể loại nhạc cổ điển.",
"Find the comments made by the user Separate-Camp7202.": "Tìm các bình luận của người dùng 'Separate-Camp7202'.",
"Find the current league leader in total blocked shots.": "Tìm cầu thủ đang dẫn đầu giải đấu về tổng số cú block.",
"Find the next available date for Albion Basin.": "Tìm ngày trống gần nhất còn nhận ở Albion Basin.",
"Get quotes for a package weighing 10 lbs with dimensions of 2 inches in length, width, and height, being shipped from Long Beach, 90802 to Portland, 97201.": "Lấy báo giá vận chuyển cho kiện hàng nặng 10 lbs, kích thước 2x2x2 inch, gửi từ Long Beach (90802) đến Portland (97201).",
"Identify the open issue with the most comments in the first trending open-source repository this week.": "Tìm issue đang mở có nhiều bình luận nhất trong repo mã nguồn mở đầu tiên đang trending tuần này.",
"Look for the best rated BBB accredited charity near 12023.": "Tìm tổ chức từ thiện được BBB chứng nhận, có đánh giá cao nhất, gần mã zip 12023.",
"Look for the largest hunting land for auction in Kansas high plain region with mineral rights posted in the last seven days.": "Tìm khu đất săn bắn lớn nhất đang đấu giá ở vùng cao nguyên Kansas, có quyền khoáng sản, đăng trong 7 ngày gần đây.",
"Open the page to learn more about how to get accredited.": "Mở trang tìm hiểu cách để được chứng nhận (accredited).",
"Open the page with an overview of the submission of releases on Discogs.": "Mở trang tổng quan về cách gửi (submit) bản phát hành trên Discogs.",
"Open the reviews of a recipe with beef sirloin.": "Mở phần đánh giá của một công thức nấu ăn dùng thịt bò sirloin.",
"Pass the first trending chess puzzle.": "Giải xong câu đố cờ vua đầu tiên đang trending.",
"Search for NordicTrack with the lowest price.": "Tìm sản phẩm NordicTrack có giá thấp nhất.",
"Search for papers related to reinforcement learning under the topics of computer science and mathematics on arxiv, with recent submission dates between September 2024 and January 2025.": "Tìm bài báo liên quan đến reinforcement learning thuộc lĩnh vực khoa học máy tính và toán học trên arxiv, nộp trong khoảng 9/2024–1/2025.",
"Search for regular weekday jobs around 14810 that I can start within two weeks or three.": "Tìm việc làm giờ hành chính các ngày trong tuần gần mã zip 14810, có thể bắt đầu trong 2–3 tuần tới.",
"Search for rentals in Corning, CA with a maximum price of $1500.": "Tìm nhà cho thuê ở Corning, CA với giá tối đa $1500.",
"See Nissan and Honda cars for sale near Kentwood, MI 49512 on CarMax.": "Xem xe Nissan và Honda đang bán gần Kentwood, MI 49512 trên CarMax.",
"Show me Diagnoses & Treatment for Female infertility.": "Cho xem thông tin chẩn đoán và điều trị vô sinh nữ.",
"Submit a request for vehicle registration renewal with title number X123456 and last 4 digits of VIN is 1234.": "Gửi yêu cầu gia hạn đăng ký xe với số title X123456 và 4 số cuối VIN là 1234.",
"Tell me information about what identification I need to bring on my trip on Amtrak.": "Cho biết cần mang theo giấy tờ tùy thân gì khi đi tàu Amtrak.",
"View the speakers that are bluetooth and wireless and filter the results to only show models that are on sale and cost less than $50.": "Xem loa bluetooth không dây, lọc kết quả chỉ hiện model đang giảm giá và dưới $50.",
}

pilot_rows = {r["item_id"] for r in csv.DictReader((ROOT/"stage1_pilot.csv").open())}
rows = list(csv.DictReader((ROOT/"stage1_all.csv").open()))
missing_vi = sorted({r["task"] for r in rows if r["task"] not in VI})
items = []
for r in rows:
    items.append({
        "id": r["item_id"],
        "en": r["task"],
        "vi": VI.get(r["task"], r["task"]),
        "png": r["png"],
        "pilot": r["item_id"] in pilot_rows,
    })
(ROOT/"items.json").write_text(json.dumps(items, ensure_ascii=False))
print("items:", len(items), "pilot:", sum(1 for i in items if i["pilot"]), "missing_vi:", missing_vi)
