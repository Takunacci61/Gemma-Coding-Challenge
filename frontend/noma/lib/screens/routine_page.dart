import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'bottom_menu.dart';

class RoutinePage extends StatefulWidget {
  @override
  _RoutinePageState createState() => _RoutinePageState();
}

class _RoutinePageState extends State<RoutinePage> {
  List<dynamic> routines = [];
  bool isLoading = true;
  String? accessToken;

  final List<String> daysOfWeek = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday',
    'Weekday',
    'Weekend',
  ];

  Future<void> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      accessToken = prefs.getString('access');
    });
  }

  Future<void> fetchRoutines() async {
    await getToken();

    try {
      final url = Uri.parse('/planner/daily-routines/');
      final response = await http.get(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
      );

      if (response.statusCode == 200) {
        setState(() {
          routines = json.decode(response.body);
          isLoading = false;
        });
      } else {
        print('Error fetching routines: ${response.statusCode}');
      }
    } catch (e) {
      print('Error: $e');
    }
  }

  Future<void> createRoutine(Map<String, dynamic> routineData) async {
    try {
      final url = Uri.parse('/planner/daily-routines/');
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
        body: jsonEncode(routineData),
      );

      if (response.statusCode == 201) {
        await fetchRoutines(); // Refresh the routines list
      } else {
        print('Error creating routine: ${response.statusCode}');
      }
    } catch (e) {
      print('Error: $e');
    }
  }

  void showRoutineDetailsModal(BuildContext context, Map<String, dynamic> routine) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: Text(
            routine['activity_name'],
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Start Time: ${routine['start_time']}'),
              SizedBox(height: 8),
              Text('End Time: ${routine['end_time']}'),
              SizedBox(height: 8),
              Text('Days: ${routine['days_of_week']}'),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text('Close'),
            ),
          ],
        );
      },
    );
  }

  void showCreateRoutineModal(BuildContext context) {
    final TextEditingController activityNameController = TextEditingController();
    TimeOfDay startTime = TimeOfDay.now();
    TimeOfDay endTime = TimeOfDay.now().replacing(hour: (TimeOfDay.now().hour + 1) % 24);
    String? selectedDay;

    showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setModalState) {
            return AlertDialog(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              title: Text('Create Routine'),
              content: SingleChildScrollView(
                child: Column(
                  children: [
                    TextField(
                      controller: activityNameController,
                      decoration: InputDecoration(
                        labelText: 'Activity Name',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                    ),
                    SizedBox(height: 10),
                    ListTile(
                      title: Text('Start Time: ${startTime.format(context)}'),
                      trailing: Icon(Icons.access_time),
                      onTap: () async {
                        final pickedTime = await showTimePicker(
                          context: context,
                          initialTime: startTime,
                        );
                        if (pickedTime != null) {
                          setModalState(() {
                            startTime = pickedTime;
                          });
                        }
                      },
                    ),
                    ListTile(
                      title: Text('End Time: ${endTime.format(context)}'),
                      trailing: Icon(Icons.access_time),
                      onTap: () async {
                        final pickedTime = await showTimePicker(
                          context: context,
                          initialTime: endTime,
                        );
                        if (pickedTime != null) {
                          setModalState(() {
                            endTime = pickedTime;
                          });
                        }
                      },
                    ),
                    SizedBox(height: 10),
                    DropdownButtonFormField<String>(
                      value: selectedDay,
                      onChanged: (value) {
                        setModalState(() {
                          selectedDay = value;
                        });
                      },
                      items: daysOfWeek.map((day) {
                        return DropdownMenuItem(
                          value: day,
                          child: Text(day),
                        );
                      }).toList(),
                      decoration: InputDecoration(
                        labelText: 'Days of the Week',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: Text('Cancel'),
                ),
                ElevatedButton(
                  onPressed: () async {
                    if (activityNameController.text.isEmpty ||
                        startTime == null ||
                        endTime == null ||
                        selectedDay == null) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Please fill out all fields')),
                      );
                      return;
                    }
                    Navigator.pop(context);
                    await createRoutine({
                      "activity_name": activityNameController.text,
                      "start_time": "${startTime.hour}:${startTime.minute}",
                      "end_time": "${endTime.hour}:${endTime.minute}",
                      "days_of_week": selectedDay,
                    });
                  },
                  child: Text('Create'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  @override
  void initState() {
    super.initState();
    fetchRoutines();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Routines'),
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
          : routines.isEmpty
          ? Center(
        child: Text(
          'No routines available',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
      )
          : ListView.builder(
        itemCount: routines.length,
        itemBuilder: (context, index) {
          final routine = routines[index];
          return Card(
            elevation: 4,
            margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            child: ListTile(
              title: Text(
                routine['activity_name'],
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Start: ${routine['start_time']}'),
                  Text('End: ${routine['end_time']}'),
                  Text('Days: ${routine['days_of_week']}'),
                ],
              ),
              trailing: Icon(Icons.arrow_forward, color: Colors.blue),
              onTap: () => showRoutineDetailsModal(context, routine),
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => showCreateRoutineModal(context),
        child: Icon(Icons.add),
        backgroundColor: Colors.blue,
      ),
      bottomNavigationBar: BottomMenu(),
    );
  }
}
