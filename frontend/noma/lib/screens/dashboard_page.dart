import 'package:flutter/material.dart';
import 'package:table_calendar/table_calendar.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

import 'bottom_menu.dart';
import 'goals_page.dart';

class DashboardPage extends StatefulWidget {
  @override
  _DashboardPageState createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  Map<String, dynamic>? dashboardData;
  bool isLoading = true;
  bool isSubmitting = false;
  String? accessToken;
  String? errorMessage;
  DateTime focusedDate = DateTime.now();

  // Fetch the access token from SharedPreferences
  Future<void> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      accessToken = prefs.getString('access');
    });
  }

  // Fetch Dashboard Data
  Future<void> fetchDashboardData() async {
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    await getToken();

    try {
      final url = Uri.parse('/planner/goals/recent/for-user/');
      final response = await http.get(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
      );

      if (response.statusCode == 200) {
        setState(() {
          dashboardData = json.decode(response.body);
          isLoading = false;
        });
      } else if (response.statusCode == 404) {
        setState(() {
          dashboardData = null;
          isLoading = false;
        });
      } else {
        setState(() {
          errorMessage = 'Error fetching dashboard data: ${response.statusCode}';
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        errorMessage = 'An error occurred while fetching dashboard data';
        isLoading = false;
      });
      print('Error: $e');
    }
  }

  // Generate Daily Plan
  Future<void> generateDailyPlan(int goalId) async {
    setState(() {
      isSubmitting = true;
      errorMessage = null;
    });

    try {
      final url = Uri.parse('planner/generate-daily-plan/$goalId/');
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
      );

      if (response.statusCode == 201) {
        await fetchDashboardData();
        setState(() {
          isSubmitting = false;
        });
      } else {
        setState(() {
          errorMessage = 'Error generating daily plan: ${response.statusCode}';
          isSubmitting = false;
        });
      }
    } catch (e) {
      setState(() {
        errorMessage = 'An error occurred while generating daily plan';
        isSubmitting = false;
      });
      print('Error: $e');
    }
  }

  // Mark activity as completed
  Future<void> markActivityCompleted(int activityId) async {
    try {
      final url = Uri.parse('/planner/daily-plan-activities-update/$activityId/');
      final response = await http.patch(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
        body: jsonEncode({"status": true}),
      );

      if (response.statusCode == 200) {
        await fetchDashboardData();
      } else {
        print('Error marking activity completed: ${response.statusCode}');
      }
    } catch (e) {
      print('Error: $e');
    }
  }

  @override
  void initState() {
    super.initState();
    fetchDashboardData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Dashboard"),
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.blue, Colors.lightBlueAccent],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
      ),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : errorMessage != null
          ? Center(
        child: Text(
          errorMessage!,
          style: TextStyle(fontSize: 16, color: Colors.red),
        ),
      )
          : dashboardData == null
          ? Center(
        child: ElevatedButton(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => GoalsPage()),
            );
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.blue,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
          ),
          child: Text('Create Goal'),
        ),
      )
          : SingleChildScrollView(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Goal Section
            Card(
              margin: EdgeInsets.only(bottom: 16.0),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              elevation: 4,
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      dashboardData!['goal_name'],
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 8),
                    Text(dashboardData!['goal_description']),
                    SizedBox(height: 8),
                    Text("Start Date: ${dashboardData!['goal_start_date']}"),
                    Text("End Date: ${dashboardData!['goal_end_date']}"),
                    SizedBox(height: 16),
                    TableCalendar(
                      firstDay: DateTime.parse(dashboardData!['goal_start_date']),
                      lastDay: DateTime.parse(dashboardData!['goal_end_date']),
                      focusedDay: focusedDate,
                      calendarFormat: CalendarFormat.month,
                      selectedDayPredicate: (day) =>
                          day.isAtSameMomentAs(DateTime.now()),
                      onDaySelected: (selectedDay, focusedDay) {
                        setState(() {
                          focusedDate = focusedDay;
                        });
                      },
                      calendarStyle: CalendarStyle(
                        todayDecoration: BoxDecoration(
                          color: Colors.blue,
                          shape: BoxShape.circle,
                        ),
                        defaultDecoration: BoxDecoration(
                          color: Colors.greenAccent,
                          shape: BoxShape.circle,
                        ),
                        weekendDecoration: BoxDecoration(
                          color: Colors.redAccent,
                          shape: BoxShape.circle,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            // Plan Section
            if (dashboardData!['daily_plans'] != null)
              Card(
                margin: EdgeInsets.only(bottom: 16.0),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                elevation: 4,
                child: Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "Plan for Today",
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 8),
                      Text(dashboardData!['daily_plans']['notes']),
                      Text("Status: ${dashboardData!['daily_plans']['status']}"),
                      SizedBox(height: 16),
                    ],
                  ),
                ),
              )
            else
              Center(
                child: ElevatedButton(
                  onPressed: () {
                    generateDailyPlan(dashboardData!['id']);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: isSubmitting
                      ? CircularProgressIndicator(strokeWidth: 2)
                      : Text('Generate Daily Plan'),
                ),
              ),
            // Activities Section
            if (dashboardData!['daily_plans'] != null &&
                dashboardData!['daily_plans']['activities'] != null)
              Card(
                margin: EdgeInsets.only(bottom: 16.0),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                elevation: 4,
                child: Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "Activities",
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 8),
                      ListView.builder(
                        shrinkWrap: true,
                        physics: NeverScrollableScrollPhysics(),
                        itemCount: dashboardData!['daily_plans']['activities'].length,
                        itemBuilder: (context, index) {
                          final activity =
                          dashboardData!['daily_plans']['activities'][index];
                          return ListTile(
                            title: Text(activity['activity_name']),
                            subtitle: Text(
                                "Start: ${activity['start_time']} - End: ${activity['end_time']}"),
                            trailing: Checkbox(
                              value: activity['status'],
                              onChanged: (value) {
                                markActivityCompleted(activity['id']);
                              },
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
      bottomNavigationBar: BottomMenu(),
    );
  }
}
