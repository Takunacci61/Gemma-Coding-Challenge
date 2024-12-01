import 'package:flutter/material.dart';
import 'dashboard_page.dart';
import 'goals_page.dart';
import 'routine_page.dart';
import 'profile_page.dart';

class BottomMenu extends StatefulWidget {
  @override
  _BottomMenuState createState() => _BottomMenuState();
}

class _BottomMenuState extends State<BottomMenu> {
  int _currentIndex = 0;

  final List<Widget> _pages = [
    DashboardPage(),
    GoalsPage(),
    RoutinePage(),
    ProfilePage(),
  ];

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
      currentIndex: _currentIndex,
      onTap: (index) {
        setState(() {
          _currentIndex = index;
        });
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => _pages[index]),
        );
      },
      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.dashboard, color: Colors.black),
          label: 'Dashboard',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.flag, color: Colors.black),
          label: 'Goals',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.calendar_today, color: Colors.black),
          label: 'Routine',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.person, color: Colors.black),
          label: 'Profile',
        ),
      ],
      selectedItemColor: Colors.black,
      unselectedItemColor: Colors.black,
      showSelectedLabels: true,
      showUnselectedLabels: true,
    );
  }
}
