import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/song.dart';

class ApiService{
  // If using Android Emulator: Use '10.0.2.2' instead of 'localhost' or '127.0.0.1'
  // If using iOS Simulator: Use '127.0.0.1'
  // If using a Real Device: Use your computer's local IP address (e.g., 192.168.1.x)
  static const String baseUrl = "http://127.0.0.1:8000";
  // static const String baseUrl = "http://10.0.2.2:8000";

  static Future<List<Song>> searchSongs(String query) async {
    try {
      final url = Uri.parse("$baseUrl/search?q=$query");
      print("Fetching: $url"); // for debugging

      final res = await http.get(url);

      if (res.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(res.body);
        
        if (data["results"] != null) {
          final List<dynamic> results = data['results'];
          return results.map((json) => Song.fromJson(json)).toList();
        }
      } else {
        print("Server Error: ${res.statusCode}");
      }
    } catch (e) {
      print("Connection Error: $e");
    }
    
    return []; // Return empty list on error so the app doesn't crash
  }
}
