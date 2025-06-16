
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_vlc_player/flutter_vlc_player.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Tapo Viewer + LINE Alert',
      home: const CameraScreen(),
    );
  }
}

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});
  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  late VlcPlayerController _vlcController;

  final String rtspUrl = "rtsp://kenny1231256:kenny28202838@192.168.0.101:554/stream1";
  final String serverUrl = "https://https://smoke-2sl6.onrender.com/alert";

  @override
  void initState() {
    super.initState();
    _vlcController = VlcPlayerController.network(
      rtspUrl,
      hwAcc: HwAcc.full,
      autoPlay: true,
      options: VlcPlayerOptions(),
    );
  }

  Future<void> sendAlert() async {
    final response = await http.post(
      Uri.parse(serverUrl),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': 'LINE_USER_ID',
        'message': '⚠️ 偵測到異常狀況！',
      }),
    );

    final snackText = response.statusCode == 200 ? '已通知 LINE' : '失敗: \${response.body}';
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(snackText)));
  }

  @override
  void dispose() {
    _vlcController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Tapo 即時影像')),
      body: Column(
        children: [
          AspectRatio(
            aspectRatio: 16 / 9,
            child: VlcPlayer(
              controller: _vlcController,
              placeholder: const Center(child: CircularProgressIndicator()),
            ),
          ),
          const SizedBox(height: 20),
          ElevatedButton.icon(
            icon: const Icon(Icons.warning),
            label: const Text('傳送警告訊息'),
            onPressed: sendAlert,
          ),
        ],
      ),
    );
  }
}
