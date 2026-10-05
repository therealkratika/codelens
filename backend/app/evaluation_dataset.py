EVALUATION_DATASET = [
    {
        "question": "How is a battle created?",
        "expected_files": [
            "backend/src/controller/battleController.js",
            "frontend/lib/api.ts",
            "frontend/components/battle/CreateBattleForm.tsx",
        ],
    },
    {
        "question": "How does a player join a battle?",
        "expected_files": [
            "backend/src/controller/battleController.js",
            "backend/src/socket/handlers/joinRoom.js",
            "frontend/components/lobby/useLobbyRoom.ts",
        ],
    },
    {
        "question": "How are battle questions selected?",
        "expected_files": [
            "backend/src/services/questionService.js",
            "backend/src/socket/handlers/startBattle.js",
            "backend/src/controller/battleController.js",
        ],
    },
    {
        "question": "How does the Socket.IO flow work?",
        "expected_files": [
            "backend/src/socket/battleSocket.js",
            "backend/src/socket/handlers/joinRoom.js",
            "frontend/components/lobby/useLobbyRoom.ts",
        ],
    },
    {
        "question": "How is a battle submission handled?",
        "expected_files": [
            "backend/src/controller/submissionController.js",
            "backend/src/routes/submissionRoutes.js",
            "frontend/lib/api.ts",
        ],
    },
]