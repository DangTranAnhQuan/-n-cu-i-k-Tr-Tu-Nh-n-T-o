# Báo cáo cuối kỳ Môn Trí Tuệ Nhân Tạo - Nhóm 10
# 1. Mục tiêu
Dự án nhằm các mục đích chính sau:

- Xây dựng một trò chơi phiêu lưu 2D hoàn chỉnh, có khả năng chơi được và mang tính giải trí.
- Chứng minh khả năng áp dụng các kiến thức và kỹ năng lập trình Pygame vào thực tế.
- Tạo ra một sản phẩm có tính hoàn thiện tốt, với đồ họa và âm thanh hấp dẫn.
- Nghiên cứu và triển khai các thuật toán tìm kiếm để cải thiện trí tuệ nhân tạo của quái vật trong việc tìm kiếm người chơi.

Các yêu cầu chính của dự án bao gồm:

- Cơ chế di chuyển và chiến đấu: Nhân vật di chuyển linh hoạt, thực hiện đa dạng hành động (chạy, nhảy, tấn công, kỹ năng, né, đỡ, hồi phục).  Hệ thống chiến đấu hỗ trợ đòn thường, kỹ năng đặc biệt với hiệu ứng hình ảnh, âm thanh.  Cơ chế va chạm chính xác và hệ thống quản lý máu, sát thương.

- Hệ thống bản đồ: Nhiều bản đồ đa dạng, tải từ tệp CSV, có cơ chế chuyển màn.    
- Hệ thống quái vật: Nhiều loại quái vật với hành vi, hình ảnh, thuộc tính riêng; có khả năng di chuyển, tấn công, bị tiêu diệt.  AI cơ bản điều khiển hành vi, bao gồm tìm đường.
  
- Hệ thống vật phẩm: Người chơi thu thập vật phẩm tăng thuộc tính (tốc độ, sức tấn công, hồi máu).
  
- Giao diện người dùng: Menu chính (chơi, cài đặt, thoát) và menu cài đặt (âm lượng) đơn giản, trực quan.
  
- Thuật toán tìm kiếm: Áp dụng các thuật toán A*, BFS, Steepest-Ascent Hill Climbing, And Or Search, Backtracking, và Q-Learning để quái vật tìm đường hiệu quả, tối ưu tài nguyên. 

# 2. Nội dung
# 2.1. Các thuật toán Tìm kiếm không có thông tin
Các thành phần chính của bài toán tìm kiếm và solution:

- Không gian trạng thái (State Space): Tập hợp tất cả các vị trí hợp lệ trên bản đồ mà một thực thể (ví dụ: quái vật) có thể chiếm giữ.
  
- Trạng thái ban đầu (Initial State): Vị trí xuất hiện đầu tiên của thực thể khi bắt đầu quá trình tìm kiếm.
  
- Hành động (Actions): Tập hợp các di chuyển mà thực thể có thể thực hiện để chuyển từ vị trí hiện tại sang vị trí mới (ví dụ: di chuyển trái, phải, lên, xuống).  Hành động chỉ hợp lệ nếu vị trí đích không phải vật cản và nằm trong bản đồ.    

- Hàm chuyển trạng thái (Transition Function): Mô tả kết quả của việc thực hiện một hành động từ một trạng thái.    

- Hàm kiểm tra đích (Goal Test): Xác định xem một trạng thái có phải là trạng thái đích hay không (ví dụ: vị trí của người chơi có đủ gần trong tầm nhìn của quái vật).    

- Hàm chi phí bước (Step Cost): Chi phí cho mỗi hành động di chuyển (trong dự án này là 1 cho mỗi bước lên, xuống, trái, phải).    

- Solution (Giải pháp): Một đường đi (path) từ trạng thái ban đầu đến trạng thái đích.  Chi phí của một đường đi là tổng chi phí các bước di chuyển trong đường đi đó.    

Một vài nhận xét về hiệu suất của các thuật toán trong nhóm này khi áp dụng lên trò chơi:

BFS (Breadth-First Search - Tìm kiếm theo chiều rộng):

- Ưu điểm: BFS đảm bảo tìm ra đường đi ngắn nhất về số bước (nếu có).  Trong dự án, thuật toán BFS hoạt động hiệu quả, giúp quái vật di chuyển một cách thông minh và tiết kiệm tài nguyên hệ thống.

- Nhược điểm: Có thể tốn kém hơn về mặt tài nguyên bộ nhớ so với các thuật toán có thông tin như A*, đặc biệt là trong các bản đồ có nhiều nhánh và đường đi khác nhau, vì nó cần lưu trữ tất cả các vị trí đã được khám phá.

# 2.2. Các thuật toán Tìm kiếm có thông tin
Các thành phần chính của bài toán tìm kiếm và solution:

- Các thành phần cơ bản của bài toán tìm kiếm (Không gian trạng thái, Trạng thái ban đầu, Hành động, Hàm chuyển trạng thái, Hàm kiểm tra đích, Hàm chi phí bước, Solution) vẫn được áp dụng như trong tìm kiếm không có thông tin.

- Điểm khác biệt chính: Thuật toán tìm kiếm có thông tin sử dụng thêm hàm heuristic (Heuristic Function) để ước tính chi phí từ trạng thái hiện tại đến trạng thái đích.  Hàm heuristic cung cấp một "ước đoán thông minh", giúp thuật toán ưu tiên các đường đi có khả năng dẫn đến mục tiêu nhanh hơn.  Trong dự án này, hàm heuristic được sử dụng là khoảng cách Manhattan.    

Một vài nhận xét về hiệu suất của các thuật toán trong nhóm này khi áp dụng lên trò chơi:
A (A Star):*

- Ưu điểm: A* thường được ưu tiên vì nó có thể tìm ra đường đi ngắn nhất (hoặc đường đi có chi phí thấp nhất) một cách hiệu quả hơn so với BFS, đặc biệt là trong các bản đồ lớn và phức tạp, nơi có nhiều ngóc ngách và đường đi khác nhau.  Trong dự án, thuật toán A* hoạt động hiệu quả, giúp quái vật di chuyển một cách thông minh và tiết kiệm tài nguyên hệ thống.    
- A* sử dụng hàng đợi ưu tiên để lưu trữ các vị trí cần xét, với ưu tiên xác định bởi tổng chi phí đã đi (g) và chi phí ước tính đến đích (h).
  
3. Kết luận
Một số kết quả đạt được khi thực hiện project này:

- Xây dựng thành công trò chơi cơ bản bằng Pygame với các chức năng cốt lõi như di chuyển nhân vật, chiến đấu, thu thập vật phẩm và điều hướng menu.    

- Ứng dụng kiến thức Trí tuệ Nhân tạo: Thể hiện khả năng ứng dụng các thuật toán tìm kiếm vào thực tế để tạo hành vi cho quái vật.    

- Tối ưu hóa hiệu suất và mã nguồn: Việc sử dụng các thuật toán tìm kiếm phù hợp (đặc biệt là A* và BFS) và thiết kế hướng đối tượng đã giúp tối ưu hóa hiệu suất và khả năng bảo trì của mã nguồn.    

- Học được cách xây dựng đồ họa nhân vật, quái vật, bản đồ, vật phẩm.

- Cơ chế di chuyển nhân vật phản hồi tốt, linh hoạt.  Hệ thống chiến đấu đa dạng, thú vị với các đòn đánh thường và kỹ năng đặc biệt.  AI của quái vật hoạt động hiệu quả trong việc tìm đường.    

- Giao diện người dùng: Hệ thống menu được thiết kế trực quan, dễ sử dụng.    

- Khắc phục lỗi và cải thiện: Một số lỗi về đồ họa, xử lý va chạm và hiệu suất đã được phát hiện và khắc phục.
