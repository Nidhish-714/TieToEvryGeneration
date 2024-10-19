import os
from flask import Flask, request, jsonify
from langchain_groq import ChatGroq
from bson.objectid import ObjectId
from sentence_transformers import SentenceTransformer, util
from pymongo.mongo_client import MongoClient
from pinecone import Pinecone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize Groq chat with the model
groq_api_key = "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"
groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name='llama-3.1-70b-versatile')

# MongoDB connection
uri = "mongodb+srv://Nidhish:Nidhish@coephackathon.pbuvv.mongodb.net/?retryWrites=true&w=majority&appName=CoepHackathon"
client = MongoClient(uri)
db = client["mytestdb"]
collection = db["mytestcollection"]

# Pinecone setup
pc = Pinecone(api_key="f68b6c67-0cfd-47b3-980b-5c29ea360fbf")
index = pc.Index("mongo")

# Load SentenceTransformer model
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def get_result(query, similar_result=1):
    embedding = embedding_model.encode(query)
    embedding = embedding.tolist()

    # Perform the query
    result = index.query(
        vector=embedding,
        top_k=similar_result,
    )

    # Filter results based on similarity score
    filtered_results = [
        match for match in result['matches'] if match['score'] > 0.5
    ]

    return filtered_results

def get_combined_information(query):
    result = get_result(query)
    mylist = []
    for match in result:  # Iterate directly over the list
        # Get the ID from the match
        value = match['id']

        # Append the found document to mylist
        document = collection.find_one({"_id": ObjectId(value)})
        if document:  # Check if the document was found
            mylist.append(document)

    # Check if mylist is empty
    if not mylist:
        return "", [], [], []  # Return empty values instead of None

    combined_information = ""
    titles = []
    fullplots = []
    file_paths = []

    for i in range(len(mylist)):
        title = mylist[i]["code_snippet"]
        fullplot = mylist[i]["fullplot"]
        file_path = mylist[i].get("file_path", "No file path available")

        titles.append(title)
        fullplots.append(fullplot)
        file_paths.append(file_path)

        combined_information += f"Code snippet: {title}\nFull plot: {fullplot}\nFile path: {file_path}\n\n"

    return combined_information, titles, fullplots, file_paths

def analyze_code_snippets(titles, file_paths):
    results = []

    for i in range(len(titles)):
        code_snippet = titles[i]
        file_path = file_paths[i]

        prompt =   f"You are an AI coding assistant. Analyze the following code snippet:\n\n"f"Code snippet:\n{code_snippet}\n"f"File path: {file_path}\n\n"f"Explain the technical guidelines and custom guidelines followed in this code."

        try:
            result = groq_chat.invoke(prompt)
            if hasattr(result, 'content'):
                clean_result = result.content.replace("\\n", "\n")
            else:
                clean_result = str(result).replace("\\n", "\n")
            results.append(clean_result)
        except Exception as e:
            results.append(f"Error analyzing code snippet at {file_path}: {str(e)}")

    return results
def analyze_code_snippets1(titles, file_paths):
    results = []

    for i in range(len(titles)):
        code_snippet = titles[i]
        file_path = file_paths[i]

        prompt =f"You are an AI coding assistant. Analyze the following code snippet:\n\n"f"Code snippet:\n{code_snippet}\n"f"File path: {file_path}\n\n","""Explain the technical guidelines ,code format and custom guidelines followed in this code. above is some good technical codeing guidlines Coding Best Practices & Guidelines to FollowThere are many coding best practices and guidelines provided to ensure that the code is clear, maintainable, and robust. Lets discuss the major practices below:1. Choose Industry-Specific Coding StandardsCoding best practices and standards vary depending on the industry a specific product is being built for. The standards required for coding software for luxury automobiles will differ from those for gaming software.For example, MISRA C and C++ were written for the automotive industry and are considered the de-facto standards for building applications that emphasize safety. They are the absolute best practices for writing code in the industry.Adhering to industry-specific coding standards in software engineering makes writing correct code that matches product expectations easier. Writing code that will satisfy the end-users and meet business requirements becomes easier.Also Read: Understanding the Software Development Process2. Focus on Code readabilityReadable code is easy to follow and optimizes space and time. Here are a few ways to achieve that:Write as few lines as possible.Use appropriate naming conventions.Segment blocks of code in the same section into paragraphs.Use indentation to mark the beginning and end of control structures. Specify the code between them.Don’t use lengthy functions. Ideally, a single function should carry out a single task.Use the DRY (Dont Repeat Yourself) principle. Automate repetitive tasks whenever necessary. The same piece of code should not be repeated in the script.Avoid Deep Nesting. Too many nesting levels make code harder to read and follow.Capitalize SQL special words and function names to distinguish them from table and column names.Avoid long lines. It is easier for humans to read blocks of lines that are horizontally short and vertically long.3. Meaningful NamesChoose meaningful names that convey the purpose of the variable or function. Consistent naming conventions enhance clarity and maintainability.// Badconst cust = "John"const customer = "Alice"// Betterconst customerName = "John"const customerFullName = "Alice Johnson"Different naming conventions used in coding –Camel Case – In camel case, you start a name with a lowercase letter. If the name has multiple words, the later words begin with capital letters. Camel case is commonly used in JavaScript for variable and function names. For Example:const userName = "Smith";                       function reverseName(name) {return name.split("").reverse().join("");}Snake Case – In snake case, you start the name with a lowercase letter. If the name has multiple words, the later words are also lowercase, and you use an underscore (_) to separate them.For Example:const user_name = "Smith";Kebab Case – Kebab case is similar to snake case, but you use a hyphen (-) instead of an underscore (_) to separate the words.For Example:const user-name = "Smith";Pascal Case (Upper Camel Case): – Names in pascal case start with a capital letter. For names with multiple words, all words begin with capital letters. Pascal case is typically used for class names in both Python and JavaScript.For Example:class Person {constructor(firstName, lastName) {this.firstName = firstName;this.lastName = lastName;    }}4. Avoid using a Single Identifier for multiple purposesAscribe a name to each variable that clearly describes its purpose. A single variable can’t be assigned various values or utilized for numerous functions. This would confuse everyone reading the code and make future enhancements more challenging. Always assign unique variable names.When the same variable or function name is used to represent different concepts or purposes within the code, it can lead to confusion, bugs, and unintended behavior.For Example:function outerFunction() {    let count = 10;    function innerFunction() {        // Oops! This 'count' shadows the outer one.        const count = 20;        console.log(count);    }    innerFunction();    console.log(count);  // Prints 10, not 20}5. Add Comments and Prioritize DocumentationComments serve as a form of documentation within the code, explaining the logic, functionality, or purpose of specific sections. Well-placed comments transform complex algorithms or intricate business rules into understandable pieces of information.For Example:// TODO: Refactor this function for better performancefunction processItems(items) {// ... existing logic ...// TODO: Optimize the sorting algorithmitems.sort((a, b) => a.value - b.value);if (items.length === 0) {console.warn("Empty items array!");    }}When to add comments:Include comments for intricate or non-obvious code segments.Explain business rules, domain-specific logic, or regulatory requirements.Clarify how your code handles edge cases or exceptional scenarios.Document workarounds due to limitations or external dependencies.Mark areas where improvements or additional features are needed.When Not to add comments:Avoid redundant comments that merely repeat what the code already expresses clearly.If the code’s purpose is evident (e.g., simple variable assignments), skip unnecessary comments.Remove temporary comments used for debugging once the issue is resolved.Incorrect comments can mislead other developers, so ensure accuracy.6. Efficient Data ProcessingDivide code into smaller, self-contained modules or functions for reusability and maintainability. Identify inefficient algorithms or data structures and refactor for better performance.// Modularizationfunction calculateTax(income) {    // Tax calculation logic    return income * 0.2;}// Encapsulationclass User {    constructor(name) {        this.name = name;    }    greet() {        console.log(Hello, ${this.name}!);    }}7. Effective Version Control and CollaborationEnsure all developers follow consistent coding techniques. Use automation tools for version control workflows.8. Effective Code Review and RefactoringEngage QA during refactoring to prevent new bugs. Isolate debugging from refactoring to maintain stability.// Before refactoringfunction calculateTotal(items) {    let total = 0;    for (const item of items) {        total += item.price;    }    return total;}// After refactoringfunction calculateTotal(items) {    return items.reduce((acc, item) => acc + item.price, 0);}9. Try to formalize Exception Handling‘Exception’ refers to problems, issues, or uncommon events that occur when code is run and disrupt the normal flow of execution. This either pauses or terminates program execution, a scenario that must be avoided.Exception handling is a critical aspect of programming, allowing developers to gracefully manage unexpected or erroneous situations. When an error occurs during program execution, the normal flow is disrupted, and an “exception” object containing information about the error is created. Exception handling involves responding to these exceptions effectively.However, when they do occur, use the following techniques to minimize damage to overall execution in terms of both time and dev effort:Keep the code in a try-catch block.Ensure that auto recovery has been activated and can be used.Consider that it might be an issue of software/network slowness. Wait a few seconds for the required elements to show up.Use real-time log analysis.Here are the key components of exception handling:Try block: The try block encapsulates code where an error might occur. If an exception occurs within this block, control transfers to the corresponding catch block.For Example:try {    // code that may throw an exception    const numerator = 10;    const denominator = 0; // throws a division by zero exception    const result = numerator / denominator; // skipped due to the exception    console.log("Result:", result);} catch (error) {// handle the exception    console.error("Error:", error.message); }Catch block: The catch block catches and handles exceptions thrown within the try block.For Example:try {    // ...} catch (error) {// Handle the exception    console.error("Error:", error.message); }Finally block (optional): The finally block executes regardless of whether an exception occurs or not. It is commonly used for cleanup tasks (e.g., closing files, releasing resources).For Example:try {    // ...} catch (error) {  // …} finally {// Executed always    console.log("Cleanup tasks here"); }Learn more about Exception Handling in Selenium WebDriver.10. Security and Privacy ConsiderationsExtract insights without compromising privacy. Acquire maximum insight from consented data for customer benefit.// Collect only necessary user dataconst userData = {    userId: 123,    // Other non-sensitive fields};11. Standardize Headers for Different ModulesIt is easier to understand and maintain code when the headers of different modules align with a singular format. For example, each header should contain:Module NameDate of creationName of creator of the moduleHistory of modificationSummary of what the module doesFunctions in that moduleVariables accessed by the module12. Turn Daily Backups into an instinctMultiple events can trigger data loss – system crash, dead battery, software glitch, hardware damage, etc. To prevent this, save code daily, and after every modification, no matter how minuscule it may be, back up the workflow on TFS, SVN, or any other version control mechanism.Talk to an Expert13. When choosing standards, think Closed vs. OpenConsider CERT vs. MISRA. CERT emphasizes community cooperation and participation. It offers a coding standard that is freely available as a web-based wiki.With CERT, users can comment on specific guidelines – comments are considered when the standards are reviewed and updated.On the other hand, MISRA is a set of C and C++ coding standards developed and maintained by the Motor Industry Software Reliability Association (MISRA). It is primarily considered the de-facto coding standard for embedded industries.MISRA was created and is updated by working groups according to predetermined blueprints. While secure and reliable, it is not available for free, though it admits some community feedback when implementing updates.Naturally, CERT is easier to work with. But open standards change quickly, making them hard to keep up with.However, closed standards like MISRA are better for safety-critical industries because they enforce uniformity across teams, organizations, and vendors.\n\n"""

        try:
            result = groq_chat.invoke(prompt)
            if hasattr(result, 'content'):
                clean_result = result.content.replace("\\n", "\n")
            else:
                clean_result = str(result).replace("\\n", "\n")
            results.append(clean_result)
        except Exception as e:
            results.append(f"Error analyzing code snippet at {file_path}: {str(e)}")

    return results

@app.route('/fetch-code', methods=['POST'])
def fetch_code_information():
    query = request.json.get('query')
    if not query:
        return jsonify({"error": "Please enter a valid query."}), 400

    combined_information, titles, fullplots, file_paths = get_combined_information(query)

    # Check if no suitable information was found
    if combined_information == "":
        try:
            # Prepare prompt for Groq
            promptT = (
                f"Query is {query}. You are a helpful assistant designed to assist new developers in retrieving code snippets that adhere , if provided message is related to coding then say this code is not present in Organization repositories"
                f"to the company's custom technical instructions and practices. Whenever someone asks you for help or any natural language "
                f"query, explain that you are a bot built for fetching relevant code implementations based on the company's standards. "
                f"Your job is to search through the company's various source code repositories and provide code snippets that match their "
                f"technical guidelines. Respond politely and always offer clear, concise, and accurate code examples that follow company guidelines."
            )

            result = groq_chat.invoke(promptT)

            if hasattr(result, 'content'):
                clean_result = result.content.replace("\\n", "\n")
                # Generate Markdown for clean result
                promptTMd = f"Convert the following analysis results into well-structured Markdown format. Ensure proper formatting for readability and use bullet points where appropriate. If any lists or steps are mentioned, use ordered or unordered lists as necessary. Ensure headings, subheadings, and code blocks (if applicable) are properly formatted so that the output displays cleanly when pasted into a Markdown viewer. Here is the content to format: {clean_result}"

                Mdresult = groq_chat.invoke(promptTMd)
                
                return jsonify({
                    "message": Mdresult.content if hasattr(Mdresult, 'content') else str(Mdresult)
                })

            else:
                clean_result = str(result).replace("\\n", "\n")
                return jsonify({
                    "message": clean_result
                })
        
        except Exception as e:
            # Instead of appending to result, create an error message string
            error_message = f"Couldn't find such code snippets regarding to your query:"

            promptTMd = f"Convert the following analysis results into well-structured Markdown format. Ensure proper formatting for readability and use bullet points where appropriate. If any lists or steps are mentioned, use ordered or unordered lists as necessary. Ensure headings, subheadings, and code blocks (if applicable) are properly formatted so that the output displays cleanly when pasted into a Markdown viewer. Here is the content to format: {error_message}"

            Mdresult = groq_chat.invoke(promptTMd)

            return jsonify({
                "message": Mdresult.content
            })

    # Now, we can safely analyze the code snippets since we know there are results
    analysis_results = analyze_code_snippets([titles[0]], [file_paths[0]])

    # Generate Markdown for the first analysis result
    promptTMd = f"Convert the following analysis results into well-structured Markdown format. Ensure proper formatting for readability and use bullet points where appropriate. If any lists or steps are mentioned, use ordered or unordered lists as necessary. Ensure headings, subheadings, and code blocks (if applicable) are properly formatted so that the output displays cleanly when pasted into a Markdown viewer. Here is the content to format: {analysis_results}"

    Mdresult = groq_chat.invoke(promptTMd)
    analy1 = [Mdresult.content if hasattr(Mdresult, 'content') else str(Mdresult)]

    # Perform another analysis
    analysis_results1 = analyze_code_snippets1([titles[0]], [file_paths[0]])
    promptTMd1 = f"Convert the following analysis results into well-structured Markdown format. Ensure proper formatting for readability and use bullet points where appropriate. If any lists or steps are mentioned, use ordered or unordered lists as necessary. Ensure headings, subheadings, and code blocks (if applicable) are properly formatted so that the output displays cleanly when pasted into a Markdown viewer. Here is the content to format: {analysis_results1}"

    Mdresult = groq_chat.invoke(promptTMd1)
    analy2 = [Mdresult.content if hasattr(Mdresult, 'content') else str(Mdresult)]

    return jsonify({
        "combined_information": combined_information,
        "titles": titles,
        "fullplots": fullplots,
        "file_paths": file_paths,
        "analysis_results": analy1,
        "analysis_results1": analy2
    })

if __name__ == '__main__':
    app.run(debug=True)
