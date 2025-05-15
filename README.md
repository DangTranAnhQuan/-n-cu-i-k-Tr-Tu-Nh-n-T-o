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

Lý do chọn thuật toán BFS vì thuật toán đảm bảo tìm ra đường đi ngắn nhất về số bước, hữu ích trong việc kiểm tra tính kết nối hoặc trên các bản đồ nhỏ hơn nơi chi phí tính toán không quá lớn.

Hiệu suất của thuật toán đã chọn trong nhóm này khi áp dụng lên trò chơi:

BFS (Breadth-First Search - Tìm kiếm theo chiều rộng):

- Ưu điểm: BFS đảm bảo tìm ra đường đi ngắn nhất về số bước (nếu có).  Trong dự án, thuật toán BFS hoạt động hiệu quả, giúp quái vật di chuyển một cách thông minh và tiết kiệm tài nguyên hệ thống.

- Nhược điểm: Có thể tốn kém hơn về mặt tài nguyên bộ nhớ so với các thuật toán có thông tin như A*, đặc biệt là trong các bản đồ có nhiều nhánh và đường đi khác nhau, vì nó cần lưu trữ tất cả các vị trí đã được khám phá.

Dưới đây là 2 ảnh gif của thuật toán BFS tương ứng với 2 kiểu di chuyển của quái vật:
![BFS](https://github.com/DangTranAnhQuan/BaoCaoCuoiKyTTNT_Nhom10/blob/main/BFS-Normal_Enemy.gif)

![BFS](https://github.com/DangTranAnhQuan/BaoCaoCuoiKyTTNT_Nhom10/blob/main/BFS-FlyingDemon.gif)
# 2.2. Các thuật toán Tìm kiếm có thông tin
Các thành phần chính của bài toán tìm kiếm và solution:

- Các thành phần cơ bản của bài toán tìm kiếm (Không gian trạng thái, Trạng thái ban đầu, Hành động, Hàm chuyển trạng thái, Hàm kiểm tra đích, Hàm chi phí bước, Solution) vẫn được áp dụng như trong tìm kiếm không có thông tin.

- Điểm khác biệt chính: Thuật toán tìm kiếm có thông tin sử dụng thêm hàm heuristic (Heuristic Function) để ước tính chi phí từ trạng thái hiện tại đến trạng thái đích.  Hàm heuristic cung cấp một "ước đoán thông minh", giúp thuật toán ưu tiên các đường đi có khả năng dẫn đến mục tiêu nhanh hơn.  Trong dự án này, hàm heuristic được sử dụng là khoảng cách Manhattan.    

Thuật toán A* được lựa chọn vì khả năng tìm đường đi ngắn nhất (hoặc chi phí thấp nhất) một cách hiệu quả bằng cách sử dụng hàm heuristic để định hướng quá trình tìm kiếm. Trong trò chơi, điều này giúp quái vật di chuyển một cách thông minh và tự nhiên hơn, tránh việc khám phá các khu vực không cần thiết.

Hiệu suất của thuật toán đã chọn trong nhóm này khi áp dụng lên trò chơi:
A (A Star):*

- Ưu điểm: A* thường được ưu tiên vì nó có thể tìm ra đường đi ngắn nhất (hoặc đường đi có chi phí thấp nhất) một cách hiệu quả hơn so với BFS, đặc biệt là trong các bản đồ lớn và phức tạp, nơi có nhiều ngóc ngách và đường đi khác nhau.  Trong dự án, thuật toán A* hoạt động hiệu quả, giúp quái vật di chuyển một cách thông minh và tiết kiệm tài nguyên hệ thống.    
- A* sử dụng hàng đợi ưu tiên để lưu trữ các vị trí cần xét, với ưu tiên xác định bởi tổng chi phí đã đi (g) và chi phí ước tính đến đích (h).

Dưới đây là 2 ảnh gif của thuật toán A* tương ứng với 2 kiểu di chuyển của quái vật:
![Astar](https://github.com/DangTranAnhQuan/BaoCaoCuoiKyTTNT_Nhom10/blob/main/A_Star-Normal_Enemy.gif)

![Astar](https://github.com/DangTranAnhQuan/BaoCaoCuoiKyTTNT_Nhom10/blob/main/A_Start-FlyingDemon.gif)
# 2.3. Các thuật toán Tìm kiếm cục bộ (Local Search)
Thuật toán được chọn: Steepest Ascent Hill Climbing (Leo đồi dốc nhất)

Lý do chọn: Thuật toán này tìm kiếm cục bộ, cố gắng di chuyển đến trạng thái lân cận tốt nhất dựa trên hàm heuristic. Nó có thể được xem xét cho các hành vi AI rất đơn giản, ví dụ như quái vật chỉ di chuyển một bước theo hướng tốt nhất tức thời mà không cần lập kế hoạch đường đi dài.

Bản chất: Là một thuật toán tìm kiếm cục bộ, cố gắng cải thiện giải pháp hiện tại bằng cách thực hiện các bước đi đến trạng thái lân cận tốt nhất một cách lặp đi lặp lại, dựa trên hàm heuristic (ví dụ: khoảng cách Manhattan). Nó không khám phá toàn bộ không gian trạng thái.

Hiệu suất và ứng dụng trong trò chơi:
- Ưu điểm: Đơn giản để triển khai, ít tốn bộ nhớ hơn A* hay BFS. Có thể phản ứng nhanh và tìm ra hướng di chuyển hợp lý tức thời trong một số trường hợp.

- Nhược điểm: Rất dễ bị kẹt ở các điểm tối ưu cục bộ (ví dụ: quái vật đi vào ngõ cụt dù có đường vòng tốt hơn ở xa). Không đảm bảo tìm ra đường đi tối ưu toàn cục hoặc thậm chí tìm được đường đi trong mọi trường hợp phức tạp. Trong dự án, thuật toán này gặp một số lỗi với quái vật bay do không gian trạng thái lớn và không được chọn làm thuật toán tìm đường chính.

Dưới đây là 2 ảnh gif của thuật toán Steepest Ascent Hill Climbing tương ứng với 2 kiểu di chuyển của quái vật:
![Steepest Ascent Hill Climbing](https://github.com/DangTranAnhQuan/BaoCaoCuoiKyTTNT_Nhom10/blob/main/Stepest_HC-Normal_Enemy.gif)


# 2.4. Các thuật toán Tìm kiếm trong môi trường phức tạp
Thuật toán được chọn: And Or Search (Tìm kiếm AND-OR)

Lý do chọn: Thuật toán này mạnh cho các bài toán có thể phân rã thành các bài toán con với điều kiện AND và OR.

Bản chất: Được thiết kế cho các bài toán có thể phân rã thành các bài toán con, với một số yêu cầu tất cả các thành phần con phải được giải quyết (AND), trong khi số khác chỉ cần một lựa chọn được giải quyết (OR).

Hiệu suất và ứng dụng trong trò chơi:
- Ưu điểm: Mạnh mẽ cho các bài toán có cấu trúc phân rã AND-OR rõ ràng (ví dụ: lập kế hoạch phức tạp).

- Nhược điểm: Bài toán tìm đường của một quái vật đơn lẻ thường là chuỗi các lựa chọn OR, không có cấu trúc AND phức tạp. Việc áp dụng And-Or Search có thể trở nên phức tạp không cần thiết và kém hiệu quả hơn A* cho việc tìm đường đơn thuần. Trong dự án, thuật toán này bị giới hạn không gian tìm kiếm, hiệu suất không tốt và gây giật lag khi gặp quái vật dạng bay.

Dưới đây là 2 ảnh gif của thuật toán And Or Search tương ứng với 2 kiểu di chuyển của quái vật:
![AndOrSearch](https://github.com/DangTranAnhQuan/BaoCaoCuoiKyTTNT_Nhom10/blob/main/And_Or-Normal_Enemy.gif)


# 2.5. Các thuật toán Tìm kiếm trong môi trường có ràng buộc
Thuật toán được chọn: Backtracking

Lý do chọn: Thuật toán Backtracking có thể được áp dụng để giải quyết các bài toán thỏa mãn ràng buộc (Constraint Satisfaction Problems - CSPs) trong trò chơi. Ví dụ: tạo màn chơi theo ràng buộc (đảm bảo các yếu tố màn chơi như vị trí quái vật, vật phẩm, địa hình thỏa mãn các điều kiện thiết kế) hoặc lập kế hoạch hành động cho quái vật.

Bản chất: Một kỹ thuật giải thuật giải quyết các Bài toán Thỏa mãn Ràng buộc (CSPs) bằng cách xây dựng từng bước các ứng cử viên cho lời giải và loại bỏ những ứng cử viên không thể hoàn thành thành một lời giải hợp lệ.

Hiệu suất và ứng dụng trong trò chơi:
- Ưu điểm: Có thể tìm được tất cả các nghiệm và hiệu quả trong các bài toán có không gian tìm kiếm nhỏ. Có thể hữu ích cho việc tạo màn chơi theo ràng buộc.

- Nhược điểm: Bài toán tìm đường của quái vật đòi hỏi quyết định nhanh chóng trong thời gian thực. Backtracking, với bản chất thử và sai, có thể không đủ hiệu quả. Việc mô hình hóa bài toán tìm đường như một CSP có thể phức tạp và không tự nhiên bằng các thuật toán tìm đường chuyên dụng. Trong dự án, nó không được xem là giải pháp chính cho tìm đường của quái vật do yêu cầu về tốc độ và có thể vẽ ra đường đi, tuy nhiên cũng gặp tình trạng giật lag khi tiếp cận quái vật dạng bay theo hướng bên dưới và bên trên.

Dưới đây là 2 ảnh gif của thuật toán Backtracking tương ứng với 2 kiểu di chuyển của quái vật:
![Backtracking](https://github.com/DangTranAnhQuan/BaoCaoCuoiKyTTNT_Nhom10/blob/main/Backtracking-Normal_Enemy.gif)

# 2.6. Thuật toán học tăng cường (Reinforcement Learning)
Thuật toán được chọn: Q-Learning

Lý do chọn: Thuật toán Q-Learning (một thuật toán học tăng cường) có thể được áp dụng để huấn luyện hành vi của quái vật. Ví dụ: quái vật có thể học các chiến lược chiến đấu hiệu quả hoặc học cách di chuyển tối ưu trong các môi trường phức tạp.

Bản chất: Một thuật toán học tăng cường không cần mô hình để học một chiến lược hành động tối ưu. Agent (quái vật) học một hàm Q(s, a) đại diện cho "chất lượng" của việc thực hiện hành động 'a' trong trạng thái 's' thông qua tương tác với môi trường và nhận phần thưởng/hình phạt.

Hiệu suất và ứng dụng trong trò chơi:
- Ưu điểm: Không cần mô hình môi trường trước và có thể học các chiến lược phức tạp.

- Nhược điểm: Đòi hỏi lượng lớn dữ liệu (tương tác) để học các giá trị Q tối ưu, có thể tốn thời gian và tài nguyên trong môi trường trò chơi thời gian thực. Việc xác định hàm phần thưởng phù hợp và các tham số (tốc độ học, hệ số chiết khấu) đòi hỏi thử nghiệm kỹ lưỡng. Trong dự án, do phạm vi và yêu cầu về giải pháp tìm đường trực tiếp, Q-Learning không được triển khai làm thuật toán chính cho việc tìm đường của quái vật, dù được nghiên cứu về khả năng áp dụng.

Dưới đây là ảnh gif của thuật toán Q-Learning tương ứng với 2 kiểu di chuyển của quái vật:


# 3. Kết luận
Một số kết quả đạt được khi thực hiện project này:

- Xây dựng thành công trò chơi cơ bản bằng Pygame với các chức năng cốt lõi như di chuyển nhân vật, chiến đấu, thu thập vật phẩm và điều hướng menu.    

- Ứng dụng kiến thức Trí tuệ Nhân tạo: Thể hiện khả năng ứng dụng các thuật toán tìm kiếm vào thực tế để tạo hành vi cho quái vật.    

- Tối ưu hóa hiệu suất và mã nguồn: Việc sử dụng các thuật toán tìm kiếm phù hợp (đặc biệt là A* và BFS) và thiết kế hướng đối tượng đã giúp tối ưu hóa hiệu suất và khả năng bảo trì của mã nguồn.    

- Học được cách xây dựng đồ họa nhân vật, quái vật, bản đồ, vật phẩm.

- Cơ chế di chuyển nhân vật phản hồi tốt, linh hoạt.  Hệ thống chiến đấu đa dạng, thú vị với các đòn đánh thường và kỹ năng đặc biệt.  AI của quái vật hoạt động hiệu quả trong việc tìm đường.    

- Giao diện người dùng: Hệ thống menu được thiết kế trực quan, dễ sử dụng.    

- Khắc phục lỗi và cải thiện: Một số lỗi về đồ họa, xử lý va chạm và hiệu suất đã được phát hiện và khắc phục.
