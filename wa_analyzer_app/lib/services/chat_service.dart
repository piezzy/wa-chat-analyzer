import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ChatService {
  static const String _baseUrl = 'http://10.0.2.2:8000';

  static Future<Map<String, dynamic>> analyzeChatFile({
    required File file,
    required String user,
  }) async {
    try {
      if (!await file.exists()) {
        throw Exception('File tidak ditemukan di perangkat');
      }

      await file.readAsString().catchError((_) {
        throw Exception('File tidak bisa dibaca');
      });

      final uri = Uri.parse('$_baseUrl/analyze');
      var request = http.MultipartRequest('POST', uri);

      request.files.add(
        await http.MultipartFile.fromPath(
          'chat',
          file.path,
          filename: 'whatsapp_chat.txt',
        ),
      );

      request.fields['user'] = user;

      final response = await request.send();

      if (response.statusCode != 200) {
        throw Exception('Server error: ${response.statusCode}');
      }

      final responseBody = await response.stream.bytesToString();
      return json.decode(responseBody) as Map<String, dynamic>;
    } on http.ClientException {
      throw Exception('Tidak bisa terhubung ke server');
    } catch (e) {
      throw Exception('Error: ${e.toString()}');
    }
  }
}