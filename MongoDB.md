# MongoDB

## Collections in the Database

1. **Authentication:**
Contains data used to authenticate Operations Team and other Systems with the API
2. **Club Teams:**
Contains data related to different team members of a club
3. **Clubs:**
Contains data about the clubs themselves
4. **Events:**
Contains data about the different events that are planned or have happened
5. **Students:**
Contains general data about students and their club affiliations

## Document Structure
### Authentication
Operations Team
```js
{
	"_id": {
		"$oid": ""
	},
	"friendly_name": "",
	"username": "",
	"auth_type": "USER",
	"password_hash": {
		"$binary": {
			"base64": "",                   // Hash of the password as bytes
			"subType": "00"
		}
	},
	"student_id": {
		"$oid": ""                          // Links to Document in Students collection
	},
	"team_id": {
		"$oid": ""                          // Links to Document in Club Teams collection
	}
}
```
Automation
```js
{
	"_id": {
		"$oid": ""
	},
	"app_id": "",
	"friendly_name": "",
	"token": {
		"$binary": {
			"base64": "",                   // Hash of Token as bytes
			"subType": "00"
		}
	},
	"auth_type": "AUTOMATION"
}
```


### Club Teams
User with API Access
```js
{
	"_id": {
		"$oid": ""
	},
	"club": "",
	"position": {
		"type": "",                         // Internal OR Core
		"name": ""
	},
	"api_access": true,
	"permissions": {
		"create_event": true,
		"modify_event": true,
		"delete_event": true,
		"get_event": true,
		"mark_attendance": true,
		"modify_attendace": true
	},
	"auth": {
		"$oid": ""                          // Links to Document in Authentication collection
	},
	"student_id": {
		"$oid": ""                          // Links to Document in Students collection
	}
}
```
User without API access
```js
{
	"_id": {
		"$oid": ""
	},
	"club": "",
	"position": {
		"type": "",                         // Internal OR Core
		"name": ""
	},
	"api_access": false,
	"student_id": {
		"$oid": ""                          // Links to Document in Students collection
	}
}
```

### Clubs
```js
{
	"_id": {
		"$oid": ""
	},
	"name": "",                             // Official Name of the entity
	"slug": "",                             // Slug used to refer to entity
	"institution": "",                      // College affiliated with
	"unit_type": "",                        // If the entity is a "Club" or a "Chapter" or a "Society"
	"events": {
		"2023": [                           // List of Events that were planned for the academic year
			{
				"$oid": ""
			}
		]
	},
	"faculty_advisors": [                   // List of Club Sponsors / Faculty Advisors
		{
			"name": "",
			"email": ""
		}
	],
	"team": [                               // Contains internal positions which are not recognised by the college
		{
			"$oid": ""                      // Links to Document in Club Teams collection
		},
		{
			"$oid": ""                      // Links to Document in Club Teams collection
		}
	],
	"core_committee": {                     // Contains positions recognised by the college
		"president": {
			"$oid": ""                      // Links to Document in Club Teams collection
		},
		"vice_president": {
			"$oid": ""                      // Links to Document in Club Teams collection
		},
		"executive_secretary": {
			"$oid": ""                      // Links to Document in Club Teams collection
		},
		"general_secretary": {
			"$oid": ""                      // Links to Document in Club Teams collection
		},
		"operations_lead": {
			"$oid": ""                      // Links to Document in Club Teams collection
		},
		"treasurer": {
			"$oid": ""                      // Links to Document in Club Teams collection
		}
	}
}
```

### Events
```js
{
	"_id": {
		"$oid": ""
	},
	"club": "",                             // Slug of Club
	"date": {
		"$date": ""
	},
	"location": "",                         // String formatted as "Building-Room"
	"name": "",                             // Formatted Name of event
	"slug": "",                             // Slug used to refer to event
	"participants": {
		"registered": [                     // List of Document IDs of Students who registered for the event
			{
				"$oid": ""
			}
		],
		"attended": [                       // List of Document IDs of Students who Attended
			{
				"$oid": ""
			}
		],
		"onspot": [                         // List of all Students who attended event but had not registered
			{
				"$oid": ""
			}
		]
	},
	"sort_year": "2023"                     // The academic year in which event took place
}
```

### Students
```js
{
	"_id": {
		"$oid": ""
	},
	"application_number": "",
	"email": "",
	"institution": "",
	"academic": {
		"stream": "",
		"year_pass": ""
	},
	"clubs": [                              // Array of Clubs of which the Student is a member
		{
			"$oid": ""
		}
	],
	"events": [                             // Array of Events the Student has taken part in OR registered for
		{
			"event_id": {
				"$oid": ""                  // Document IDs of Event
			},
			"registration": "",             // Time of Registeration OR "on-spot"
			"attendance": "",               // Boolean showing if the student attended the event or not
			"sort_year": ""                 // The academic year in which event took place
		}
	],
	"phone_number": "",
	"registration_number": "",
	"name": "",
	"mess_provider": ""
}
```
