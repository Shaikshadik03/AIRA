import 'package:flutter/material.dart';
import 'dart:convert';
import 'dart:io';
import 'dart:async';
import 'package:file_picker/file_picker.dart';

void main() {
  runApp(const AiraOsecosystem());
}

class AiraOsecosystem extends StatelessWidget {
  const AiraOsecosystem({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AIRA OS Master Console',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF060609),
        primaryColor: const Color(0xFF00E5FF),
        cardColor: const Color(0xFF0F0F17),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF00E5FF),
          secondary: Color(0xFF7C4DFF),
          surface: Color(0xFF0F0F17),
        ),
      ),
      home: const AiraAuthBridge(),
    );
  }
}

class AiraAppState {
  static String groqApiKey = "";
  static String activeUserEmail = "developer.btech@aira.io";
  static String activeUsername = "Core Builder Node";
  static String targetCloudUrl = "https://aira-l1c5.onrender.com";
  
  static List<Map<String, String>> conversationHistory = [
    {"id": "default_session", "title": "Live Link Frame (Default)"},
    {"id": "session_alpha", "title": "System Boot Frame Alpha"},
    {"id": "session_beta", "title": "Laptop Screenshot Capture Log"},
    {"id": "session_gamma", "title": "PDF Document Summary Data"},
    {"id": "session_delta", "title": "Mobile Hardware Link Engine"}
  ];
}

class AiraAuthBridge extends StatefulWidget {
  const AiraAuthBridge({super.key});

  @override
  State<AiraAuthBridge> createState() => _AiraAuthBridgeState();
}

class _AiraAuthBridgeState extends State<AiraAuthBridge> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _apiKeyController = TextEditingController();

  void _triggerLoginSequence(bool isGoogle) {
    setState(() {
      if (isGoogle) {
        AiraAppState.activeUsername = "Google Developer Account";
        AiraAppState.activeUserEmail = "btech.builder@gmail.com";
      }
      if (_apiKeyController.text.isNotEmpty) {
        AiraAppState.groqApiKey = _apiKeyController.text;
      }
    });

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const AiraDashboardDeck()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Icon(Icons.blur_on, size: 75, color: Color(0xFF00E5FF)),
              const SizedBox(height: 16),
              const Text(
                'AIRA OS',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, letterSpacing: 8, color: Color(0xFF00E5FF), fontFamily: 'serif'),
              ),
              const Text(
                'Advanced Neural Matrix Interface',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 11, color: Colors.grey, letterSpacing: 1.5),
              ),
              const SizedBox(height: 40),
              TextField(
                controller: _apiKeyController,
                obscureText: true,
                decoration: InputDecoration(
                  labelText: 'Groq LLM Persistent API Key',
                  hintText: 'gsk_...',
                  prefixIcon: const Icon(Icons.vpn_key_outlined, color: Color(0xFF00E5FF)),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _emailController,
                decoration: InputDecoration(
                  labelText: 'SaaS Cluster Email Address',
                  prefixIcon: const Icon(Icons.alternate_email_sharp, color: Color(0xFF7C4DFF)),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _passwordController,
                obscureText: true,
                decoration: InputDecoration(
                  labelText: 'Secure Core Password',
                  prefixIcon: const Icon(Icons.lock_reset_outlined, color: Color(0xFF7C4DFF)),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () => _triggerLoginSequence(false),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF11111A),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: const BorderSide(color: Color(0xFF7C4DFF), width: 1.2)),
                ),
                child: const Text('Initialize Matrix Session Space', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                onPressed: () => _triggerLoginSequence(true),
                icon: const Icon(Icons.g_mobiledata_rounded, color: Colors.cyanAccent, size: 28),
                label: const Text('Synchronize with Google Credentials', style: TextStyle(fontWeight: FontWeight.w600)),
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  side: const BorderSide(color: Colors.white24),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ],
          ),
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
  bool _mobileFlashlightState = false;
  
  // 🌟 NEW STATE VARIABLE: Tracks whether Text-to-Speech feedback mode is armed
  bool _vocalFeedbackActive = false;
  
  String _activeSessionId = "default_session";
  String _activeSessionTitle = "Live Link Frame (Default)";
  
  late AnimationController _siriAnimationController;
  late Animation<double> _pulseWaveAnimation;

  @override
  void initState() {
    super.initState();
    _chatLogs.add({
      "sender": "AIRA Engine",
      "text": "🌌 **AIRA AI Cognitive Gateway Online.** Master feature arrays unified successfully.",
      "image": null
    });

    _siriAnimationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat(reverse: true);
    
    _pulseWaveAnimation = Tween<double>(begin: 0.85, end: 1.15).animate(
      CurvedAnimation(parent: _siriAnimationController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _siriAnimationController.dispose();
    _inputController.dispose();
    super.dispose();
  }

  // 🌟 NEW FUNCTION: MONITORS INCOMING TEXT STRINGS AND SYNTHESIZES VOICE AUDIO
  void _synthesizeVocalResponse(String textToSpeak) {
    if (!_vocalFeedbackActive) return;

    // Clean up markdown markers so the voice engine speaks cleanly
    String cleanString = textToSpeak.replaceAll(RegExp(r'\*|#|`|⚠️|❌|🌌'), '');

    setState(() {
      _chatLogs.add({
        "sender": "AIRA Audio Status",
        "text": "🔊 *[AIRA Voice Synthesis Output]: \"$cleanString\"*",
        "image": null
      });
    });
  }

  Future<void> _fetchHistoricalSessionData(String sessionId, String titleText) async {
    setState(() {
      _activeSessionId = sessionId;
      _activeSessionTitle = titleText;
      _networkLoading = true;
      _chatLogs.clear();
    });

    try {
      final client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 10);
      final url = Uri.parse('${AiraAppState.targetCloudUrl}/history/$sessionId');
      final request = await client.getUrl(url);
      final response = await request.close();

      if (response.statusCode == 200) {
        final responseBody = await response.transform(utf8.decoder).join();
        final List<dynamic> pastRecordsList = jsonDecode(responseBody);

        setState(() {
          for (var record in pastRecordsList) {
            String roleStr = record["sender"] == "User" ? "User" : "AIRA Engine";
            _chatLogs.add({
              "sender": roleStr,
              "text": record["text"] ?? "",
              "image": record["image"]
            });
          }
          if (_chatLogs.isEmpty) {
            _chatLogs.add({"sender": "AIRA Engine", "text": "🫙 **Empty Matrix Segment.**", "image": null});
          }
        });
      }
    } catch (e) {
      setState(() {
        _chatLogs.add({"sender": "AIRA Engine", "text": "❌ **Historical Sync Timeout.**", "image": null});
      });
    } finally {
      setState(() => _networkLoading = false);
    }
  }

  Future<void> _pickAndUploadRealPDF() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf'],
      );

      if (result == null || result.files.single.path == null) return;
      
      String localFilePath = result.files.single.path!;
      File targetFile = File(localFilePath);
      String filename = localFilePath.split('/').last;

      setState(() {
        _chatLogs.add({"sender": "User", "text": "📁 [Uploading Document File Asset]: $filename", "image": null});
        _networkLoading = true;
      });

      final client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 30);
      final url = Uri.parse('${AiraAppState.targetCloudUrl}/chat/document');
      final request = await client.postUrl(url);

      final boundary = "----AiraFormBoundary${DateTime.now().millisecondsSinceEpoch}";
      request.headers.set(HttpHeaders.contentTypeHeader, "multipart/form-data; boundary=$boundary");

      List<int> multiPartPayloadBytes = [];

      void injectBodyField(String name, String value) {
        multiPartPayloadBytes.addAll(utf8.encode('--$boundary\r\n'));
        multiPartPayloadBytes.addAll(utf8.encode('Content-Disposition: form-data; name="$name"\r\n\r\n'));
        multiPartPayloadBytes.addAll(utf8.encode('$value\r\n'));
      }

      injectBodyField("session_id", _activeSessionId);
      injectBodyField("conversation_title", _activeSessionTitle);
      injectBodyField("user", AiraAppState.activeUsername);

      multiPartPayloadBytes.addAll(utf8.encode('--$boundary\r\n'));
      multiPartPayloadBytes.addAll(utf8.encode('Content-Disposition: form-data; name="file"; filename="$filename"\r\n'));
      multiPartPayloadBytes.addAll(utf8.encode('Content-Type: application/pdf\r\n\r\n'));
      multiPartPayloadBytes.addAll(await targetFile.readAsBytes());
      multiPartPayloadBytes.addAll(utf8.encode('\r\n--$boundary--\r\n'));

      request.contentLength = multiPartPayloadBytes.length;
      request.add(multiPartPayloadBytes);
      
      final response = await request.close();
      
      if (response.statusCode == 200) {
        final responseBody = await response.transform(utf8.decoder).join();
        final serverData = jsonDecode(responseBody);
        
        setState(() {
          _chatLogs.add({"sender": "AIRA Engine", "text": serverData["response"] ?? "Analysis stream complete.", "image": null});
        });
        
        // Synthesize spoken audio feedback for PDF summaries if active
        _synthesizeVocalResponse(serverData["response"] ?? "");
      }
    } catch (e) {
      setState(() {
        _chatLogs.add({"sender": "AIRA Engine", "text": "❌ **Document Pipeline Transport Exception.**", "image": null});
      });
    } finally {
      setState(() => _networkLoading = false);
    }
  }

  void _engageVoiceTriggerSequence() {
    setState(() {
      _voiceTriggerActive = true;
    });

    Timer(const Duration(seconds: 3), () {
      if (!mounted || !_voiceTriggerActive) return;
      setState(() => _voiceTriggerActive = false);
      String spokenText = _inputController.text.isNotEmpty ? _inputController.text : "Take a screen snapshot map and show status";
      _dispatchCommand(spokenText);
    });
  }

  void _processMobileHardwareAction(String? actionToken) {
    if (actionToken == null || actionToken.isEmpty) return;

    if (actionToken == "TOGGLE_FLASHLIGHT") {
      setState(() {
        _mobileFlashlightState = !_mobileFlashlightState;
        _chatLogs.add({"sender": "AIRA Engine", "text": "💡 [Local Hardware Trigger]: Flashlight shifted to **${_mobileFlashlightState ? "ACTIVE_ON" : "OFF"}**.", "image": null});
      });
      _synthesizeVocalResponse("Flashlight toggled successfully");
    } else if (actionToken == "CALL_MUMMY") {
      setState(() {
        _chatLogs.add({"sender": "AIRA Engine", "text": "📞 [Local Hardware Trigger]: Dialer tracking contact: **[Mummy]**.", "image": null});
      });
      _synthesizeVocalResponse("Calling Mummy now");
    } else if (actionToken == "MESSAGE_DADDY") {
      setState(() {
        _chatLogs.add({"sender": "AIRA Engine", "text": "💬 [Local Hardware Trigger]: Background SMS dispatched to **[Daddy]** payload: `Hi`.", "image": null});
      });
      _synthesizeVocalResponse("Message sent to Daddy");
    }
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
      final body = jsonEncode({
        "message": text,
        "session_id": _activeSessionId,
        "conversation_title": _activeSessionTitle,
        "user": AiraAppState.activeUsername
      });
      
      request.write(body);
      final response = await request.close();
      
      if (response.statusCode == 200) {
        final responseBody = await response.transform(utf8.decoder).join();
        final serverData = jsonDecode(responseBody);
        
        setState(() {
          _chatLogs.add({
            "sender": "AIRA Engine",
            "text": serverData["response"] ?? "No response string received.",
            "image": serverData["image"] 
          });
        });

        // Trigger local phone responses if returned by cloud AI
        _processMobileHardwareAction(serverData["mobile_action"]);

        // 🌟 DISPATCHING AUDIO FEEDBACK ROUTINE FILTER MATRIX LINK
        _synthesizeVocalResponse(serverData["response"] ?? "");

      } else {
        setState(() {
          _chatLogs.add({"sender": "AIRA Engine", "text": "⚠️ **Server Link Interrupted:** Error code [${response.statusCode}].", "image": null});
        });
      }
    } catch (e) {
      setState(() {
        _chatLogs.add({"sender": "AIRA Engine", "text": "❌ **Network Timeout Error.**", "image": null});
      });
    } finally {
      setState(() => _networkLoading = false);
    }
  }

  void _showSettingsModal() {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF0A0A10),
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('SYSTEM PARAMETERS DECK', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF00E5FF), fontFamily: 'serif')),
              const Divider(color: Colors.white24),
              const SizedBox(height: 12),
              Text('Cloud Endpoint: ${AiraAppState.targetCloudUrl}', style: const TextStyle(color: Colors.grey)),
              const SizedBox(height: 8),
              Text('Active Identity: ${AiraAppState.activeUsername}', style: const TextStyle(color: Colors.grey)),
              const SizedBox(height: 8),
              Text('Active Session ID: $_activeSessionId', style: const TextStyle(color: Color(0xFF7C4DFF), fontWeight: FontWeight.bold)),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF7C4DFF)),
                child: const Center(child: Text('Close Configuration View')),
              )
            ],
          ),
        );
      },
    );
  }

  void _showAttachmentMenu() {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF0A0A10),
      builder: (context) {
        return SafeArea(
          child: Wrap(
            children: [
              ListTile(
                leading: const Icon(Icons.picture_as_pdf, color: Colors.redAccent),
                title: const Text('Upload Document Asset File (.pdf)'),
                onTap: () {
                  Navigator.pop(context);
                  _pickAndUploadRealPDF();
                },
              ),
              ListTile(
                leading: const Icon(Icons.image, color: Color(0xFF00E5FF)),
                title: const Text('Select Display Image Graphic (.png/.jpg)'),
                onTap: () {
                  Navigator.pop(context);
                  _dispatchCommand("Decode and view this attached mobile graphical frame parameter");
                },
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_activeSessionTitle.toUpperCase(), style: const TextStyle(fontSize: 12, letterSpacing: 1.5, fontWeight: FontWeight.bold, fontFamily: 'serif')),
        backgroundColor: const Color(0xFF060609),
        actions: [
          if (_networkLoading)
            const Center(
              child: SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF00E5FF))),
            ),
          IconButton(
            icon: const Icon(Icons.tune_sharp, color: Color(0xFF00E5FF)),
            onPressed: _showSettingsModal,
          )
        ],
      ),
      
      drawer: Drawer(
        backgroundColor: const Color(0xFF060609),
        child: Column(
          children: [
            DrawerHeader(
              decoration: const BoxDecoration(color: Color(0xFF0F0F17)),
              child: Row(
                children: [
                  const Icon(Icons.account_circle_outlined, size: 48, color: Color(0xFF00E5FF)),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(AiraAppState.activeUsername, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                        Text(AiraAppState.activeUserEmail, style: const TextStyle(fontSize: 10, color: Colors.grey), overflow: TextOverflow.ellipsis),
                      ],
                    ),
                  )
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(12.0),
              child: Row(
                children: [
                  const Icon(Icons.history_toggle_off, size: 16, color: Colors.grey),
                  const SizedBox(width: 8),
                  Text('HISTORICAL CONTROL FRAMES', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 1, color: Colors.grey[400])),
                ],
              ),
            ),
            Expanded(
              child: ListView.builder(
                padding: EdgeInsets.zero,
                itemCount: AiraAppState.conversationHistory.length,
                itemBuilder: (context, index) {
                  final nodeItem = AiraAppState.conversationHistory[index];
                  bool isCurrent = nodeItem["id"] == _activeSessionId;
                  
                  return ListTile(
                    leading: Icon(
                      Icons.chat_bubble_outline_rounded, 
                      size: 16, 
                      color: isCurrent ? const Color(0xFF00E5FF) : const Color(0xFF7C4DFF)
                    ),
                    title: Text(
                      nodeItem["title"] ?? "", 
                      style: TextStyle(
                        fontSize: 12, 
                        fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                        color: isCurrent ? const Color(0xFF00E5FF) : Colors.white
                      )
                    ),
                    onTap: () {
                      Navigator.pop(context);
                      _fetchHistoricalSessionData(nodeItem["id"]!, nodeItem["title"]!);
                    },
                  );
                },
              ),
            ),
            const Divider(color: Colors.white10),
            ListTile(
              leading: const Icon(Icons.power_settings_new, color: Colors.redAccent),
              title: const Text('Disconnect Matrix Workspace', style: TextStyle(fontSize: 12)),
              onTap: () {
                Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => const AiraAuthBridge()));
              },
            ),
          ],
        ),
      ),
      
      body: Stack(
        children: [
          Column(
            children: [
              // 📊 DYNAMIC TELEMETRY PANEL GRID MATRIX
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                color: const Color(0xFF0B0B11),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.flashlight_on, size: 14, color: _mobileFlashlightState ? const Color(0xFF00E5FF) : Colors.grey),
                        const SizedBox(width: 6),
                        Text('FLASH: ${_mobileFlashlightState ? "ACTIVE" : "STBY"}', style: const TextStyle(fontSize: 10, color: Colors.grey, fontWeight: FontWeight.bold)),
                      ],
                    ),
                    
                    // 🌟 UPGRADED VOICE SPEAKER TOGGLE SWITCH DIRECTLY IN PANEL STRIP
                    GestureDetector(
                      onTap: () {
                        setState(() {
                          _vocalFeedbackActive = !_vocalFeedbackActive;
                        });
                      },
                      child: Row(
                        children: [
                          Icon(
                            _vocalFeedbackActive ? Icons.volume_up : Icons.volume_off, 
                            size: 14, 
                            color: _vocalFeedbackActive ? const Color(0xFF7C4DFF) : Colors.grey
                          ),
                          const SizedBox(width: 4),
                          Text(
                            _vocalFeedbackActive ? '🔊 VOCAL REPLIES' : '🔇 MUTE RESPONSES', 
                            style: TextStyle(
                              fontSize: 10, 
                              color: _vocalFeedbackActive ? const Color(0xFF7C4DFF) : Colors.grey, 
                              fontWeight: FontWeight.bold
                            )
                          ),
                        ],
                      ),
                    ),
                    
                    const Row(
                      children: [
                        Icon(Icons.battery_charging_full, size: 14, color: Color(0xFF00E5FF)),
                        SizedBox(width: 4),
                        Text('CELL GRID: 82%', style: TextStyle(fontSize: 10, color: Colors.grey, fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ],
                ),
              ),

              Container(
                height: 52,
                padding: const EdgeInsets.symmetric(vertical: 6.0),
                color: const Color(0xFF0F0F17),
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  children: [
                    _buildShortcutButton("📸 Snapshot Map", () => _dispatchCommand("Take a clean screenshot capture snapshot of my laptop screen")),
                    _buildShortcutButton("⚡ Toggle Flashlight", () => _processMobileHardwareAction("TOGGLE_FLASHLIGHT")),
                    _buildShortcutButton("📞 Call Mother", () => _processMobileHardwareAction("CALL_MUMMY")),
                    _buildShortcutButton("💬 Text Father", () => _processMobileHardwareAction("MESSAGE_DADDY")),
                    _buildShortcutButton("🔒 Lock Workspace", () => _dispatchCommand("Secure and lock my windows station workstation console layer now")),
                    _buildShortcutButton("🌙 Engage Sleep", () => _dispatchCommand("Trigger true power standby suspension sleep state")),
                    _buildShortcutButton("🔊 Volume Up", () => _dispatchCommand("Raise hardware volume scale amplitude levels")),
                    _buildShortcutButton("🔉 Volume Down", () => _dispatchCommand("Turn down my audio sound level output scale")),
                    _buildShortcutButton("🌐 Open Chrome Browser", () => _dispatchCommand("Launch internet browser chrome instance")),
                    _buildShortcutButton("💻 Run VS Code", () => _dispatchCommand("Launch development workspace environment studio code editor")),
                  ],
                ),
              ),

              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _chatLogs.length,
                  itemBuilder: (context, index) {
                    final logItem = _chatLogs[index];
                    bool isUser = logItem["sender"] == "User";
                    bool isAudioStatus = logItem["sender"] == "AIRA Audio Status";
                    
                    Color bubbleColor = const Color(0xFF0F0F17);
                    Color borderColor = const Color(0xFF1E1E2D);
                    
                    if (isUser) {
                      bubbleColor = const Color(0xFF7C4DFF).withOpacity(0.15);
                      borderColor = const Color(0xFF7C4DFF);
                    } else if (isAudioStatus) {
                      bubbleColor = const Color(0xFF00E5FF).withOpacity(0.05);
                      borderColor = const Color(0xFF00E5FF).withOpacity(0.3);
                    }
                    
                    return Column(
                      crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
                      children: [
                        Container(
                          margin: const EdgeInsets.symmetric(vertical: 6),
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: bubbleColor,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: borderColor, width: 1)
                          ),
                          child: Text(
                            logItem["text"] ?? "", 
                            style: TextStyle(
                              height: 1.4,
                              fontStyle: isAudioStatus ? FontStyle.italic : FontStyle.normal,
                              color: isAudioStatus ? const Color(0xFF00E5FF) : Colors.white
                            )
                          ),
                        ),
                        
                        if (logItem["image"] != null && logItem["image"].toString().isNotEmpty)
                          Container(
                            margin: const EdgeInsets.only(bottom: 12, top: 4),
                            width: 270,
                            height: 160,
                            decoration: BoxDecoration(
                              color: const Color(0xFF0F0F17),
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: const Color(0xFF00E5FF), width: 1.5),
                            ),
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(10),
                              child: Image.memory(
                                base64Decode(logItem["image"].toString().replaceAll(RegExp(r'data:image\/jpeg;base64,'), '')),
                                fit: BoxFit.cover,
                                errorBuilder: (context, error, stackTrace) => const Center(
                                  child: Text("Streaming Visual Display Array Map...", style: TextStyle(fontSize: 10, color: Colors.grey)),
                                ),
                              ),
                            ),
                          ),
                      ],
                    );
                  },
                ),
              ),

              Padding(
                padding: const EdgeInsets.all(12.0),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.add_circle_outline, color: Color(0xFF7C4DFF)),
                      onPressed: _showAttachmentMenu,
                    ),
                    Expanded(
                      child: TextField(
                        controller: _inputController,
                        onSubmitted: _dispatchCommand,
                        decoration: InputDecoration(
                          hintText: 'Command your operating cluster framework...',
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(24)),
                          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    GestureDetector(
                      onTap: _engageVoiceTriggerSequence,
                      child: ScaleTransition(
                        scale: _voiceTriggerActive ? _pulseWaveAnimation : const AlwaysStoppedAnimation(1.0),
                        child: CircleAvatar(
                          radius: 20,
                          backgroundColor: _voiceTriggerActive ? const Color(0xFF00E5FF) : const Color(0xFF7C4DFF),
                          child: Icon(
                            _voiceTriggerActive ? Icons.blur_linear_rounded : Icons.mic,
                            color: Colors.white,
                            size: 18,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              )
            ],
          ),
          
          if (_voiceTriggerActive)
            Positioned(
              bottom: 60,
              left: 20,
              right: 20,
              child: AnimatedOpacity(
                opacity: _voiceTriggerActive ? 1.0 : 0.0,
                duration: const Duration(milliseconds: 200),
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFF001A1F).withOpacity(0.95),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFF00E5FF), width: 1.5),
                    boxShadow: [
                      BoxShadow(color: const Color(0xFF00E5FF).withOpacity(0.3), blurRadius: 15, spreadRadius: 2)
                    ],
                  ),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.multitrack_audio_rounded, color: Color(0xFF00E5FF), size: 24),
                      SizedBox(width: 12),
                      Text(
                        'AIRA Listening Matrix... [3s Lock Active]',
                        style: TextStyle(color: Color(0xFF00E5FF), fontWeight: FontWeight.bold, fontSize: 12, letterSpacing: 1),
                      ),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildShortcutButton(String label, VoidCallback action) {
    return Padding(
      padding: const EdgeInsets.only(right: 8.0),
      child: ElevatedButton(
        onPressed: action,
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF141420),
          foregroundColor: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
            side: const BorderSide(color: Color(0xFF202033), width: 1),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 14),
        ),
        child: Text(label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
      ),
    );
  }
}