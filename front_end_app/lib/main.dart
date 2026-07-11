import 'package:flutter/material.dart';
import 'dart:convert';
import 'dart:io';
import 'dart:async';
import 'package:file_picker/file_picker.dart';
import 'package:speech_to_text/speech_to_text.dart'; // 🎙️ Speech recognition engine

void main() {
  runApp(const AiraOsecosystem());
}

class AiraOsecosystem extends StatelessWidget {
  const AiraOsecosystem({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AIRA Intelligence Console',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF121214), // Premium deep dark screen
        primaryColor: const Color(0xFFD4C5B9), // Elegant stone cream accent
        cardColor: const Color(0xFF1A1A1E),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFFE6E4E2),
          secondary: Color(0xFF9F9285),
          surface: Color(0xFF1A1A1E),
        ),
      ),
      home: const AiraAuthBridge(),
    );
  }
}

class AiraAppState {
  static String groqApiKey = "";
  static String activeUserEmail = "";
  static String activeUsername = "";
  static bool isLoggedIn = false;
  static String targetCloudUrl = "https://aira-l1c5.onrender.com";
  
  static List<Map<String, String>> conversationHistory = [
    {"id": "default_session", "title": "Initial System Analysis Framework"},
    {"id": "session_alpha", "title": "Core System Memory Mapping"},
    {"id": "session_beta", "title": "Document Vector Verification String"}
  ];
}

class AiraAuthBridge extends StatefulWidget {
  const AiraAuthBridge({super.key});

  @override
  State<AiraAuthBridge> createState() => _AiraAuthBridgeState();
}

class _AiraAuthBridgeState extends State<AiraAuthBridge> {
  bool _authenticating = false;

  void _simulateGoogleSignSequence() async {
    setState(() => _authenticating = true);
    await Future.delayed(const Duration(milliseconds: 1200));
    
    AiraAppState.isLoggedIn = true;
    AiraAppState.activeUsername = "Developer Core Identity";
    AiraAppState.activeUserEmail = "shaik.developer@gmail.com";
    
    setState(() => _authenticating = false);

    if (mounted) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const AiraDashboardDeck()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 40.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'AIRA AI',
              style: TextStyle(fontSize: 42, fontFamily: 'serif', fontWeight: FontWeight.w400, color: Color(0xFFE6E4E2)),
            ),
            const SizedBox(height: 12),
            Text('Welcome to your unified operation terminal dashboard.', style: TextStyle(fontSize: 14, color: Colors.grey[400], height: 1.5)),
            const SizedBox(height: 60),
            _authenticating 
              ? const Center(child: CircularProgressIndicator(color: Color(0xFF9F9285)))
              : InkWell(
                  onTap: _simulateGoogleSignSequence,
                  borderRadius: BorderRadius.circular(8),
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    decoration: BoxDecoration(border: Border.all(color: const Color(0xFF2E2E34), width: 1.5), borderRadius: BorderRadius.circular(8), color: const Color(0xFF1A1A1E)),
                    child: const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.g_mobiledata_rounded, size: 28, color: Colors.white),
                        SizedBox(width: 12),
                        Text('Continue with Google Account', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: Colors.white)),
                      ],
                    ),
                  ),
                ),
          ],
        ),
      ),
    );
  }
}

class AiraDashboardDeck extends StatefulWidget {
  const AiraDashboardDeck({super.key});

  @override
  State<AiraDashboardDeck> createState() => _AiraDashboardDeckState();
}

class _AiraDashboardDeckState extends State<AiraDashboardDeck> with SingleTickerProviderStateMixin {
  final List<Map<String, dynamic>> _chatLogs = [];
  final _inputController = TextEditingController();
  bool _voiceTriggerActive = false;
  bool _networkLoading = false;
  
  // 🎙️ Speech Status State Parameters
  final SpeechToText _speechEngine = SpeechToText();
  bool _speechEngineReady = false;
  
  String _activeSessionId = "default_session";
  String _activeSessionTitle = "Initial System Analysis Framework";
  
  late AnimationController _voiceRippleController;
  late Animation<double> _voiceRippleScale;

  @override
  void initState() {
    super.initState();
    _chatLogs.add({
      "sender": "AIRA",
      "text": "How can I assist your operation system workflow sequence today?",
      "image": null
    });

    _voiceRippleController = AnimationController(vsync: this, duration: const Duration(milliseconds: 900))..repeat(reverse: true);
    _voiceRippleScale = Tween<double>(begin: 0.90, end: 1.10).animate(CurvedAnimation(parent: _voiceRippleController, curve: Curves.easeInOut));
    
    // Auto-initialize the passive background microphone loop
    _initializeAlwaysListeningVoiceCore();
  }

  @override
  void dispose() {
    _voiceRippleController.dispose();
    _inputController.dispose();
    super.dispose();
  }

  // 🎙️ Continuous background micro-listener initialization
  void _initializeAlwaysListeningVoiceCore() async {
    try {
      bool available = await _speechEngine.initialize(
        onStatus: (status) {
          // Restart microphone capture loop if it stops naturally
          if (status == 'notListening' && AiraAppState.isLoggedIn) {
            _startPassiveBackgroundListeningLoop();
          }
        },
        onError: (error) => debugPrint("Speech Core Alert: $error"),
      );
      
      if (available) {
        setState(() => _speechEngineReady = true);
        _startPassiveBackgroundListeningLoop();
      }
    } catch (e) {
      debugPrint("Speech Ingestion Exception: $e");
    }
  }

  // 🎙️ Passive background listening monitor logic loop
  void _startPassiveBackgroundListeningLoop() {
    if (!_speechEngineReady || _voiceTriggerActive) return;

    _speechEngine.listen(
      onResult: (result) {
        String wordsParsed = result.recognizedWords.toLowerCase();
        
        // ⚡ WAKE WORD CRITERIA CHECK
        if (wordsParsed.contains("hey aira") || wordsParsed.contains("aira")) {
          _speechEngine.stop(); // Pause engine loop briefly to isolate inputs
          _engageVoiceTriggerSequence();
        }
      },
      listenFor: const Duration(seconds: 30),
      pauseFor: const Duration(seconds: 10),
      partialResults: true,
      cancelOnError: false,
    );
  }

  void _engageVoiceTriggerSequence() {
    if (_voiceTriggerActive) return;

    setState(() {
      _voiceTriggerActive = true;
    });

    // Handle text parsing exact layout timing window
    Timer(const Duration(seconds: 3), () {
      if (!mounted || !_voiceTriggerActive) return;
      setState(() => _voiceTriggerActive = false);
      
      String textToSend = _inputController.text.isNotEmpty 
          ? _inputController.text 
          : "Take a clean screenshot capture snapshot of my laptop desktop monitor frame screen array now";
      
      _dispatchCommand(textToSend);
      
      // Resume primary listening array
      _startPassiveBackgroundListeningLoop();
    });
  }

  void _dispatchCommand(String text) async {
    if (text.trim().isEmpty) return;

    setState(() {
      _chatLogs.add({"sender": "User", "text": text, "image": null});
      _networkLoading = true;
    });
    _inputController.clear();

    try {
      final client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 12);
      final url = Uri.parse('${AiraAppState.targetCloudUrl}/chat');
      final request = await client.postUrl(url);
      
      request.headers.contentType = ContentType.json;
      request.write(jsonEncode({
        "message": text,
        "session_id": _activeSessionId,
        "conversation_title": _activeSessionTitle,
        "user": AiraAppState.activeUsername,
        "persistent_key_override": AiraAppState.groqApiKey
      }));
      
      final response = await request.close();
      if (response.statusCode == 200) {
        final responseBody = await response.transform(utf8.decoder).join();
        final serverData = jsonDecode(responseBody);
        
        setState(() {
          _chatLogs.add({
            "sender": "AIRA",
            "text": serverData["response"] ?? "",
            "image": serverData["image"] 
          });
        });
      }
    } catch (e) {
      setState(() {
        _chatLogs.add({"sender": "AIRA", "text": "Communication bridge transmission interruption.", "image": null});
      });
    } finally {
      setState(() => _networkLoading = false);
    }
  }

  void _showProfessionalSettingsDock() {
    final keyController = TextEditingController(text: AiraAppState.groqApiKey);

    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF16161A),
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(16))),
      builder: (context) {
        return Padding(
          padding: EdgeInsets.only(top: 24, left: 24, right: 24, bottom: MediaQuery.of(context).viewInsets.bottom + 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Console Settings', style: TextStyle(fontSize: 20, fontFamily: 'serif', color: Colors.white, fontWeight: FontWeight.w500)),
              const SizedBox(height: 4),
              Text('Manage secure keys and environment pipeline credentials.', style: TextStyle(color: Colors.grey[500], fontSize: 13)),
              const Divider(color: Colors.white10, height: 32),
              const Text('Groq API Authentication Token', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.white70)),
              const SizedBox(height: 8),
              TextField(
                controller: keyController,
                obscureText: true,
                decoration: InputDecoration(
                  hintText: 'gsk_...',
                  filled: true,
                  fillColor: const Color(0xFF1E1E24),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide.none),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () {
                  setState(() {
                    AiraAppState.groqApiKey = keyController.text.trim();
                  });
                  Navigator.pop(context);
                },
                style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFE6E4E2), foregroundColor: Colors.black, minimumSize: const Size.fromHeight(48), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8))),
                child: const Text('Save Framework Parameters', style: TextStyle(fontWeight: FontWeight.bold)),
              )
            ],
          ),
        );
      },
    );
  }

  Future<void> _pickAndUploadRealPDF() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(type: FileType.custom, allowedExtensions: ['pdf']);
      if (result == null || result.files.single.path == null) return;
      
      String localFilePath = result.files.single.path!;
      File targetFile = File(localFilePath);
      String filename = localFilePath.split('/').last;

      setState(() {
        _chatLogs.add({"sender": "User", "text": "Ingesting document reference map: $filename", "image": null});
        _networkLoading = true;
      });

      final client = HttpClient();
      final url = Uri.parse('${AiraAppState.targetCloudUrl}/chat/document');
      final request = await client.postUrl(url);

      final boundary = "----AiraFormBoundary${DateTime.now().millisecondsSinceEpoch}";
      request.headers.set(HttpHeaders.contentTypeHeader, "multipart/form-data; boundary=$boundary");

      List<int> multiPartPayloadBytes = [];
      void injectBodyField(String name, String value) {
        multiPartPayloadBytes.addAll(utf8.encode('--$boundary\r\nContent-Disposition: form-data; name="$name"\r\n\r\n$value\r\n'));
      }

      injectBodyField("session_id", _activeSessionId);
      injectBodyField("conversation_title", _activeSessionTitle);
      injectBodyField("user", AiraAppState.activeUsername);

      multiPartPayloadBytes.addAll(utf8.encode('--$boundary\r\nContent-Disposition: form-data; name="file"; filename="$filename"\r\nContent-Type: application/pdf\r\n\r\n'));
      multiPartPayloadBytes.addAll(await targetFile.readAsBytes());
      multiPartPayloadBytes.addAll(utf8.encode('\r\n--$boundary--\r\n'));

      request.contentLength = multiPartPayloadBytes.length;
      request.add(multiPartPayloadBytes);
      final response = await request.close();
      
      if (response.statusCode == 200) {
        final responseBody = await response.transform(utf8.decoder).join();
        final serverData = jsonDecode(responseBody);
        setState(() {
          _chatLogs.add({"sender": "AIRA", "text": serverData["response"] ?? "", "image": null});
        });
      }
    } catch (e) {
      setState(() {
        _chatLogs.add({"sender": "AIRA", "text": "Document ingestion execution breakdown parameter interruption.", "image": null});
      });
    } finally {
      setState(() => _networkLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_activeSessionTitle, style: const TextStyle(fontSize: 15, fontFamily: 'serif', fontWeight: FontWeight.w400, color: Color(0xFFE6E4E2))),
        backgroundColor: const Color(0xFF121214),
        elevation: 0,
        leading: Builder(
          builder: (context) => IconButton(
            icon: const Icon(Icons.menu_open_sharp, color: Color(0xFF9F9285)),
            onPressed: () => Scaffold.of(context).openDrawer(),
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined, color: Color(0xFF9F9285)),
            onPressed: _showProfessionalSettingsDock,
          ),
        ],
      ),
      
      drawer: Drawer(
        backgroundColor: const Color(0xFF121214),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.only(top: 60, left: 24, bottom: 24),
              child: Text(AiraAppState.activeUsername, style: const TextStyle(fontSize: 18, fontFamily: 'serif', color: Colors.white, fontWeight: FontWeight.w400)),
            ),
            const Divider(color: Colors.white10, indent: 24, endIndent: 24),
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                itemCount: AiraAppState.conversationHistory.length,
                itemBuilder: (context, index) {
                  final nodeItem = AiraAppState.conversationHistory[index];
                  bool isCurrent = nodeItem["id"] == _activeSessionId;
                  
                  return ListTile(
                    title: Text(
                      nodeItem["title"] ?? "",
                      style: TextStyle(fontSize: 13, fontFamily: 'serif', color: isCurrent ? const Color(0xFFE6E4E2) : Colors.grey[500], fontWeight: isCurrent ? FontWeight.w500 : FontWeight.w400),
                    ),
                    onTap: () {
                      Navigator.pop(context);
                      setState(() {
                        _activeSessionId = nodeItem["id"]!;
                        _activeSessionTitle = nodeItem["title"]!;
                        _chatLogs.clear();
                        _chatLogs.add({"sender": "AIRA", "text": "Context shifted space dynamic frame loaded.", "image": null});
                      });
                    },
                  );
                },
              ),
            ),
            const Divider(color: Colors.white10),
            ListTile(
              leading: const Icon(Icons.logout_outlined, color: Colors.grey, size: 18),
              title: const Text('Exit Terminal', style: TextStyle(fontSize: 13, color: Colors.grey)),
              onTap: () {
                AiraAppState.isLoggedIn = false;
                _speechEngine.stop();
                Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => const AiraAuthBridge()));
              },
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
      
      body: Stack(
        children: [
          Column(
            children: [
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                  itemCount: _chatLogs.length,
                  itemBuilder: (context, index) {
                    final logItem = _chatLogs[index];
                    bool isUser = logItem["sender"] == "User";
                    
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            isUser ? 'YOU' : 'AIRA',
                            style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, letterSpacing: 1.2, color: isUser ? const Color(0xFF9F9285) : const Color(0xFFD4C5B9)),
                          ),
                          const SizedBox(height: 8),
                          Text(logItem["text"] ?? "", style: const TextStyle(fontSize: 15, fontFamily: 'serif', color: Color(0xFFECEAE8), height: 1.6)),
                          if (logItem["image"] != null && logItem["image"].toString().isNotEmpty)
                            Container(
                              margin: const EdgeInsets.only(top: 16),
                              width: double.infinity,
                              height: 200,
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(8),
                                image: DecorationImage(
                                  image: MemoryImage(base64Decode(logItem["image"].toString().replaceAll(RegExp(r'data:image\/jpeg;base64,'), ''))),
                                  fit: BoxFit.cover,
                                ),
                              ),
                            ),
                        ],
                      ),
                    );
                  },
                ),
              ),

              if (_networkLoading)
                const Padding(
                  padding: EdgeInsets.only(bottom: 16.0),
                  child: SizedBox(width: 24, height: 2, child: LinearProgressIndicator(color: Color(0xFF9F9285), backgroundColor: Colors.transparent)),
                ),

              Padding(
                padding: const EdgeInsets.only(left: 20, right: 20, bottom: 28),
                child: Container(
                  decoration: BoxDecoration(color: const Color(0xFF1A1A1E), borderRadius: BorderRadius.circular(24), border: Border.all(color: const Color(0xFF2E2E34), width: 1)),
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  child: Row(
                    children: [
                      IconButton(
                        icon: const Icon(Icons.add_circle_outline_sharp, color: Color(0xFF9F9285), size: 22),
                        onPressed: _pickAndUploadRealPDF,
                      ),
                      Expanded(
                        child: TextField(
                          controller: _inputController,
                          onSubmitted: _dispatchCommand,
                          style: const TextStyle(fontSize: 14, fontFamily: 'serif', color: Colors.white),
                          decoration: const InputDecoration(
                            hintText: 'Ask anything or command system...',
                            hintStyle: TextStyle(color: Colors.grey, fontSize: 14, fontFamily: 'serif'),
                            border: InputBorder.none,
                            contentPadding: EdgeInsets.symmetric(horizontal: 8, vertical: 10),
                          ),
                        ),
                      ),
                      GestureDetector(
                        onTap: _engageVoiceTriggerSequence,
                        child: ScaleTransition(
                          scale: _voiceTriggerActive ? _voiceRippleScale : const AlwaysStoppedAnimation(1.0),
                          child: Container(
                            margin: const EdgeInsets.all(4),
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(shape: BoxShape.circle, color: _voiceTriggerActive ? const Color(0xFFD4C5B9) : const Color(0xFF2E2E34)),
                            child: Icon(
                              _voiceTriggerActive ? Icons.blur_linear_rounded : Icons.mic_none_outlined,
                              color: _voiceTriggerActive ? Colors.black : Colors.white,
                              size: 18,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          
          if (_voiceTriggerActive)
            Positioned(
              bottom: 100,
              left: 24,
              right: 24,
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 20),
                decoration: BoxDecoration(
                  color: const Color(0xFF16161A),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF9F9285), width: 1),
                  boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.4), blurRadius: 12, offset: const Offset(0, 4))],
                ),
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.waves_sharp, color: Color(0xFFD4C5B9), size: 20),
                    SizedBox(width: 12),
                    Text('Listening for voice stream command...', style: TextStyle(color: Colors.white, fontSize: 13, fontFamily: 'serif', letterSpacing: 0.5)),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}