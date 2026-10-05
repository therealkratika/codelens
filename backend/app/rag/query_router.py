class QueryRouter:

    FLOW_KEYWORDS = {
        "api",
        "apis",
        "endpoint",
        "endpoints",
        "route",
        "routes",
        "request",
        "requests",
        "response",
        "responses",
        "backend",
        "architecture",
        "flow",
        "flows",
        "trace",
        "tracing",
        "dependency",
        "dependencies",
        "call",
        "calls",
        "communication",
        "socket",
        "socketio",
        "authentication",
        "authenticate",
        "login",
        "logout",
        "signup",
        "register",
        "database",
        "databases",
        "create",
        "created",
        "creating",
        "creation",
        "build",
        "built",
        "building",
        "update",
        "updating",
        "delete",
        "deleting",
        "join",
        "joining",
        "leave",
        "leaving",
        "submit",
        "submitting",
    }

    def classify(self, question):

        question_lower = question.lower()

        normalized = (
            question_lower
            .replace("?", " ")
            .replace(",", " ")
            .replace(".", " ")
            .replace(":", " ")
            .replace("/", " ")
            .replace("-", " ")
        )

        words = set(
            normalized.split()
        )

        if words.intersection(
            self.FLOW_KEYWORDS
        ):
            return "feature_flow"

        return "code_explanation"