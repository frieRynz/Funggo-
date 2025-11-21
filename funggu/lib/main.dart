import 'package:flutter/material.dart';
import 'screens/landing_page.dart';

void main() {
  runApp(const FunggoApp());
}

class FunggoApp extends StatelessWidget {
  const FunggoApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FungGo!',
      theme: ThemeData(
        primarySwatch: Colors.deepOrange,
        scaffoldBackgroundColor: const Color(0xFFF5F5F5),
        fontFamily: 'Arial',
      ),
      home: const LandingPage(),
      debugShowCheckedModeBanner: false,
    );
  }
}