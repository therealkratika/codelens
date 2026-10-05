FEATURE_FLOW_DATASET = [
    {
        "name": "createBattle",
        "route": "POST /api/battle/create",
        "controller_file": "backend/src/controller/battleController.js",
        "controller_function": "createBattle",
        "expected_dependencies": {
            "Battle": "backend/src/model/battle.js",
            "generateUniqueRoomCode": "backend/src/utils/generateRoomCode.js",
        },
    },
    {
        "name": "joinBattle",
        "route": "POST /api/battle/join",
        "controller_file": "backend/src/controller/battleController.js",
        "controller_function": "joinBattle",
        "expected_dependencies": {
            "Battle": "backend/src/model/battle.js",
        },
    },
    {
        "name": "getBattleQuestions",
        "route": "GET /api/battle/:roomCode/questions",
        "controller_file": "backend/src/controller/battleController.js",
        "controller_function": "getBattleQuestions",
        "expected_dependencies": {
            "Battle": "backend/src/model/battle.js",
            "Question": "backend/src/model/question.js",
            "sanitizeQuestion": "backend/src/services/questionService.js",
        },
    },
]