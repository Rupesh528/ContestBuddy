# screens/cp_guide.py
import flet as ft
from services.cpp_compiler_service import CPPCompilerService, get_learning_path, get_cpp_basics, SAMPLE_PROBLEMS
import threading

def cp_guide_page(page: ft.Page, navigate_to):
    page.title = "Competitive Programming Guide"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20
    
    # Initialize compiler service
    compiler_service = CPPCompilerService()
    
    # UI Components
    header = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda _: navigate_to("/"),
                    icon_color=ft.Colors.BLUE_900,
                ),
                ft.Text(
                    "🚀 Competitive Programming Guide",
                    weight=ft.FontWeight.BOLD,
                    size=20,
                    color=ft.Colors.BLUE_900,
                ),
            ],
            spacing=10
        ),
        padding=10,
        bgcolor=ft.Colors.BLUE_50,
        border_radius=ft.border_radius.only(
            bottom_left=10,
            bottom_right=10,
        ),
    )
    
    # Tabs for different sections
    tab_content = ft.Container()
    
    def create_basics_tab():
        """Create the basics tutorial tab."""
        basics = get_cpp_basics()
        
        content = ft.Column([
            ft.Text("📚 C++ Basics for Competitive Programming", 
                    size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
            ft.Container(height=10),
        ])
        
        for section_key, section in basics.items():
            content.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(section["title"], size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(section["content"], size=14),
                        ]),
                        padding=15,
                    ),
                    margin=ft.margin.symmetric(vertical=5),
                )
            )
        
        return ft.Container(
            content=content,
            padding=10,
        )
    
    def create_learning_path_tab():
        """Create the learning path tab."""
        learning_path = get_learning_path()
        
        content = ft.Column([
            ft.Text("🎯 Learning Path", 
                    size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
            ft.Container(height=10),
        ])
        
        for level_key, level in learning_path.items():
            level_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(level["title"], size=16, weight=ft.FontWeight.BOLD),
                        ft.Text("Topics to Cover:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Column([
                            ft.Text(f"• {topic}", size=12) 
                            for topic in level["topics"]
                        ]),
                        ft.Container(height=10),
                        ft.Text(f"Practice Problems: {len(level['problems'])}", 
                               size=12, color=ft.Colors.GREEN_700),
                    ]),
                    padding=15,
                ),
                margin=ft.margin.symmetric(vertical=5),
            )
            content.controls.append(level_card)
        
        return ft.Container(
            content=content,
            padding=10,
        )
    
    def create_code_editor():
        """Create code editor with compilation feature."""
        code_editor = ft.TextField(
            multiline=True,
            min_lines=15,
            max_lines=25,
            value='''#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}''',
            text_style=ft.TextStyle(font_family="Courier New"),
            hint_text="Write your C++ code here...",
        )
        
        input_field = ft.TextField(
            multiline=True,
            min_lines=3,
            max_lines=5,
            hint_text="Program input (if needed)...",
            label="Input"
        )
        
        output_field = ft.TextField(
            multiline=True,
            min_lines=5,
            max_lines=10,
            read_only=True,
            hint_text="Output will appear here...",
            label="Output"
        )
        
        compile_button = ft.ElevatedButton(
            "🔨 Compile & Run",
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_600,
            ),
            height=45,
        )
        
        loading_indicator = ft.ProgressRing(visible=False)
        
        def compile_code(e):
            """Compile and run the code."""
            if not code_editor.value.strip():
                output_field.value = "Error: No code to compile!"
                page.update()
                return
            
            # Show loading
            compile_button.disabled = True
            loading_indicator.visible = True
            output_field.value = "Compiling..."
            page.update()
            
            def run_compilation():
                try:
                    result = compiler_service.compile_and_run(
                        code_editor.value,
                        input_field.value or ""
                    )
                    
                    if result["success"]:
                        output_text = f"✅ Compilation Successful!\n\n"
                        if result["output"]:
                            output_text += f"Output:\n{result['output']}\n"
                        if result["error"]:
                            output_text += f"\nWarnings/Errors:\n{result['error']}\n"
                        if result.get("time"):
                            output_text += f"\nExecution Time: {result['time']}s"
                        if result.get("memory"):
                            output_text += f"\nMemory Used: {result['memory']} KB"
                    else:
                        output_text = f"❌ Compilation Failed!\n\nError:\n{result['error']}"
                    
                    output_field.value = output_text
                    
                except Exception as ex:
                    output_field.value = f"❌ Error: {str(ex)}"
                
                finally:
                    # Hide loading
                    compile_button.disabled = False
                    loading_indicator.visible = False
                    page.update()
            
            # Run compilation in background thread
            threading.Thread(target=run_compilation).start()
        
        compile_button.on_click = compile_code
        
        return ft.Column([
            ft.Text("💻 Code Editor & Compiler", 
                    size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
            ft.Container(height=10),
            ft.Text("Write your C++ code:", size=14),
            code_editor,
            ft.Container(height=10),
            input_field,
            ft.Container(height=10),
            ft.Row([
                compile_button,
                loading_indicator,
            ], alignment=ft.MainAxisAlignment.START),
            ft.Container(height=10),
            output_field,
        ])
    
    def create_problems_tab():
        """Create practice problems tab."""
        problems_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=10,
        )
        
        def load_problem_in_editor(problem):
            """Load a problem's starter code in the editor tab."""
            # Switch to editor tab and load the code
            tabs.selected_index = 2
            tab_content.content = create_code_editor()
            # Find the code editor and set its value
            editor_column = tab_content.content
            code_editor = editor_column.controls[2]  # The TextField for code
            code_editor.value = problem["starter_code"]
            
            # Also set sample input
            input_field = editor_column.controls[4]  # The input TextField
            input_field.value = problem["sample_input"]
            
            page.update()
        
        # Track which solutions are unlocked
        unlocked_solutions = {}
        
        def create_problem_card(problem, index):
            """Create a problem card with hidden solution."""
            
            # Solution container that will be shown/hidden
            solution_container = ft.Container(
                visible=False,  # Initially hidden
                content=ft.Column([
                    ft.Container(height=10),
                    ft.Text("💡 Solution:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                    ft.Container(
                        content=ft.Text(
                            problem["solution"], 
                            size=12, 
                            font_family="Courier New",
                            selectable=True,
                        ),
                        bgcolor=ft.Colors.GREEN_50,
                        border_radius=5,
                        border=ft.border.all(1, ft.Colors.GREEN_300),
                        padding=10,
                    ),
                    ft.Container(height=5),
                    ft.Text("📝 Explanation:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                    ft.Container(
                        content=ft.Text(problem["explanation"], size=13),
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=5,
                        border=ft.border.all(1, ft.Colors.BLUE_300),
                        padding=10,
                    ),
                ])
            )
            
            # Unlock button
            unlock_button = ft.ElevatedButton(
                "🔓 Show Solution & Explanation",
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.ORANGE_600,
                ),
                height=40,
            )
            
            def toggle_solution(e):
                """Toggle solution visibility."""
                if solution_container.visible:
                    # Hide solution
                    solution_container.visible = False
                    unlock_button.text = "🔓 Show Solution & Explanation"
                    unlock_button.style.bgcolor = ft.Colors.ORANGE_600
                else:
                    # Show solution
                    solution_container.visible = True
                    unlock_button.text = "🔒 Hide Solution & Explanation"
                    unlock_button.style.bgcolor = ft.Colors.RED_600
                
                page.update()
            
            unlock_button.on_click = toggle_solution
            
            problem_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(problem["title"], size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Text(
                                    problem["difficulty"],
                                    color=ft.Colors.WHITE,
                                    size=12,
                                ),
                                bgcolor=ft.Colors.BLUE_500 if problem["difficulty"] == "Beginner" 
                                       else ft.Colors.ORANGE_500,
                                border_radius=5,
                                padding=ft.padding.all(5),
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        
                        ft.Container(height=5),
                        ft.Text(problem["description"], size=14),
                        
                        ft.Container(height=10),
                        ft.Text("Sample Input:", size=12, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Text(problem["sample_input"] or "No input", 
                                           size=12, font_family="Courier New"),
                            bgcolor=ft.Colors.GREY_100,
                            border_radius=5,
                            padding=10,
                        ),
                        
                        ft.Container(height=5),
                        ft.Text("Expected Output:", size=12, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Text(problem["expected_output"], 
                                           size=12, font_family="Courier New"),
                            bgcolor=ft.Colors.GREY_100,
                            border_radius=5,
                            padding=10,
                        ),
                        
                        ft.Container(height=10),
                        ft.Row([
                            ft.ElevatedButton(
                                "🏃 Try This Problem",
                                on_click=lambda e, p=problem: load_problem_in_editor(p),
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor=ft.Colors.GREEN_600,
                                ),
                            ),
                            ft.Container(width=10),
                            unlock_button,
                        ], wrap=True),
                        
                        # Hidden solution section
                        solution_container,
                    ]),
                    padding=15,
                ),
                margin=ft.margin.symmetric(vertical=5),
            )
            
            return problem_card
        
        # Create problem cards
        for index, problem in enumerate(SAMPLE_PROBLEMS):
            problem_card = create_problem_card(problem, index)
            problems_list.controls.append(problem_card)
        
        return ft.Column([
            ft.Text("🧩 Practice Problems", 
                    size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
            ft.Container(height=5),
            ft.Container(
                content=ft.Text(
                    "💡 Tip: Try solving each problem first before unlocking the solution!",
                    size=12,
                    color=ft.Colors.ORANGE_700,
                    italic=True,
                ),
                bgcolor=ft.Colors.ORANGE_50,
                border_radius=5,
                padding=10,
            ),
            ft.Container(height=10),
            ft.Container(
                content=problems_list,
                height=600,  # Fixed height for scrolling
            ),
        ])
    
    def on_tab_change(e):
        """Handle tab changes."""
        selected_index = e.control.selected_index
        
        if selected_index == 0:
            tab_content.content = create_basics_tab()
        elif selected_index == 1:
            tab_content.content = create_learning_path_tab()
        elif selected_index == 2:
            tab_content.content = create_code_editor()
        elif selected_index == 3:
            tab_content.content = create_problems_tab()
        
        page.update()
    
    # Create tabs
    tabs = ft.Tabs(
        selected_index=0,
        on_change=on_tab_change,
        tabs=[
            ft.Tab(text="📚 Basics", icon=ft.Icons.SCHOOL),
            ft.Tab(text="🎯 Learning Path", icon=ft.Icons.TIMELINE),
            ft.Tab(text="💻 Code Editor", icon=ft.Icons.CODE),
            ft.Tab(text="🧩 Problems", icon=ft.Icons.QUIZ),
        ]
    )
    
    # Initial content
    tab_content.content = create_basics_tab()
    
    # Main layout
    main_content = ft.Column([
        header,
        ft.Container(height=10),
        tabs,
        ft.Container(height=10),
        tab_content,
    ], expand=True)
    
    page.add(main_content)
    page.update()