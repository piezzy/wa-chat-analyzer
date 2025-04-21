import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:io';
import '../services/chat_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({Key? key}) : super(key: key);

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  File? _selectedFile = null;
  bool _isLoading = false;
  String _errorMessage = '';
  Map<String, dynamic> _analysisResults = {};

  Future<void> _pickFile() async {
    setState(() {
      _errorMessage = '';
    });

    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['txt'],
      );

      if (result == null || result.files.isEmpty) return;

      final file = File(result.files.first.path!);
      if (!await file.exists()) {
        throw Exception('File tidak ditemukan di perangkat');
      }

      setState(() {
        _selectedFile = file;
        _analysisResults = {};
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Error: ${e.toString()}';
      });
    }
  }

  Future<void> _analyzeFile() async {
    if (_selectedFile == null) {
      setState(() => _errorMessage = 'Pilih file terlebih dahulu');
      return;
    }

    if (!await _selectedFile!.exists()) {
      setState(() => _errorMessage = 'File tidak bisa diakses');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    try {
      final results = await ChatService.analyzeChatFile(
        file: _selectedFile!,
        user: 'User1',
      );

      setState(() {
        _analysisResults = results;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Analisis gagal: ${e.toString()}';
      });
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Analisis WhatsApp')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            ElevatedButton(
              onPressed: _isLoading ? null : _pickFile,
              child: const Text('PILIH FILE'),
            ),

            const SizedBox(height: 12),

            if (_selectedFile != null)
              Text(
                'File: ${_selectedFile!.path.split('/').last}',
                style: TextStyle(color: Colors.blue[700]),
              ),

            const SizedBox(height: 24),

            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _analyzeFile,
                child: _isLoading
                    ? const CircularProgressIndicator()
                    : const Text('PROSES ANALISIS'),
              ),
            ),

            const SizedBox(height: 16),

            if (_errorMessage.isNotEmpty)
              Text(
                _errorMessage,
                style: const TextStyle(color: Colors.red),
              ),

            const SizedBox(height: 24),

            if (_analysisResults.isNotEmpty)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'HASIL ANALISIS:',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Text('Pesan: ${_analysisResults['num_messages'] ?? 0}'),
                  Text('Kata: ${_analysisResults['num_words'] ?? 0}'),
                  Text('Media: ${_analysisResults['media_count'] ?? 0}'),
                  Text('Link: ${_analysisResults['links'] ?? 0}'),
                ],
              ),
          ],
        ),
      ),
    );
  }
}