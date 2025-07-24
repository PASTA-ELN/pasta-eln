import os
import ast
import sys
from graphviz import Digraph

class SignalSlotAnalyzer(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.classes = {}  # class_name -> {'signals', 'slots', 'emits'}
        self.connections = []  # (signal, slot)
        self.current_class = None
        self.current_function = None
        self.imports = {}  # track imports like 'from PySide6.QtCore import Signal, Slot'

    def visit_ImportFrom(self, node):
        if node.module and 'QtCore' in node.module:
            for alias in node.names:
                self.imports[alias.name] = f"{node.module}.{alias.name}"
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.imports[alias.asname or alias.name] = alias.name
        self.generic_visit(node)

    def _is_signal_call(self, node):
        """Check if a call node represents a Signal creation"""
        if isinstance(node.func, ast.Name):
            return node.func.id == 'Signal' or node.func.id in self.imports and 'Signal' in self.imports[node.func.id]
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr == 'Signal'
        return False

    def _is_slot_decorator(self, decorator):
        """Check if a decorator represents a Slot"""
        if isinstance(decorator, ast.Name):
            return decorator.id == 'Slot' or decorator.id in self.imports and 'Slot' in self.imports[decorator.id]
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr == 'Slot'
        elif isinstance(decorator, ast.Call):
            return self._is_slot_decorator(decorator.func)
        return False

    def visit_ClassDef(self, node):
        self.current_class = node.name
        self.classes[self.current_class] = {
            'signals': set(),
            'slots': set(),
            'emits': []
        }

        for stmt in node.body:
            # Signals
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and isinstance(stmt.value, ast.Call):
                        if self._is_signal_call(stmt.value):
                            self.classes[self.current_class]['signals'].add(target.id)

            # Slots
            if isinstance(stmt, ast.FunctionDef):
                for decorator in stmt.decorator_list:
                    if self._is_slot_decorator(decorator):
                        self.classes[self.current_class]['slots'].add(stmt.name)

        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = None

    def _ast_to_string(self, node):
        """Convert AST node to string, with fallback for older Python versions"""
        if hasattr(ast, 'unparse'):
            return ast.unparse(node)
        else:
            # Fallback for Python < 3.9
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Attribute):
                return f"{self._ast_to_string(node.value)}.{node.attr}"
            else:
                return str(node)

    def visit_Call(self, node):
        # signal.connect(slot)
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'connect':
            signal_name = self._ast_to_string(node.func.value)
            if node.args:
                slot_name = self._ast_to_string(node.args[0])
                connection = {
                    'signal': signal_name,
                    'slot': slot_name,
                    'signal_class': self.current_class,
                    'file': self.filename
                }
                self.connections.append(connection)

        # signal.emit(...)
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'emit':
            signal_name = self._ast_to_string(node.func.value)
            if self.current_class:
                self.classes[self.current_class]['emits'].append({
                    'signal': signal_name,
                    'function': self.current_function,
                    'file': self.filename
                })

        self.generic_visit(node)


def analyze_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=path)
        analyzer = SignalSlotAnalyzer(path)
        analyzer.visit(tree)
        return analyzer
    except Exception as e:
        print(f"Failed to parse {path}: {e}")
        return None


def analyze_project(root_path):
    project_results = []
    for dirpath, _, filenames in os.walk(root_path):
        for file in filenames:
            if file.endswith('.py'):
                full_path = os.path.join(dirpath, file)
                result = analyze_file(full_path)
                if result:
                    project_results.append(result)
    return project_results


def generate_graph(analyzers, output_path='signal_slot_graph.dot'):
    try:
        dot = Digraph(comment='Signal-Slot Architecture', format='pdf')
        dot.attr(rankdir='TB', size='12,8')
        
        # Track all classes and their signals/slots
        all_classes = {}
        
        for analyzer in analyzers:
            for cls, data in analyzer.classes.items():
                if data['signals'] or data['slots'] or data['emits']:
                    class_id = f"{cls}_{os.path.basename(analyzer.filename).replace('.', '_')}"
                    all_classes[class_id] = {
                        'name': cls,
                        'file': os.path.basename(analyzer.filename),
                        'data': data,
                        'analyzer': analyzer
                    }
                    
                    # Create class node with signals and slots
                    signals_str = '\\n'.join([f"📡 {s}" for s in sorted(data['signals'])])
                    slots_str = '\\n'.join([f"🎯 {s}" for s in sorted(data['slots'])])
                    emits_str = '\\n'.join([f"⚡ {e['signal']}" for e in data['emits']])
                    
                    label_parts = [f"**{cls}**", f"📄 {os.path.basename(analyzer.filename)}"]
                    if signals_str:
                        label_parts.append(f"\\nSignals:\\n{signals_str}")
                    if slots_str:
                        label_parts.append(f"\\nSlots:\\n{slots_str}")
                    if emits_str:
                        label_parts.append(f"\\nEmits:\\n{emits_str}")
                    
                    dot.node(class_id, label='\\n'.join(label_parts), shape='record', 
                            style='filled', fillcolor='lightblue')

        # Add connections
        for analyzer in analyzers:
            for connection in analyzer.connections:
                signal_parts = connection['signal'].split('.')
                slot_parts = connection['slot'].split('.')
                
                # Try to match signal source to a class
                signal_class = None
                if connection['signal_class']:
                    signal_class_id = f"{connection['signal_class']}_{os.path.basename(analyzer.filename).replace('.', '_')}"
                    if signal_class_id in all_classes:
                        signal_class = signal_class_id

                # Create edge label
                edge_label = f"{connection['signal']} → {connection['slot']}"
                
                if signal_class:
                    # Find target class if possible
                    target_class = None
                    for class_id, class_info in all_classes.items():
                        if any(slot_parts[-1] in class_info['data']['slots'] for _ in [1]):
                            target_class = class_id
                            break
                    
                    if target_class and target_class != signal_class:
                        dot.edge(signal_class, target_class, label=edge_label, 
                                color='red', style='dashed')

        dot.render(output_path, view=False, cleanup=True)
        print(f"Graph saved to {output_path}.pdf")
        
    except ImportError:
        print("Error: graphviz package not installed. Install with: pip install graphviz")
        return False
    except Exception as e:
        print(f"Error generating graph: {e}")
        return False
    
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyseSignals.py <path-to-your-project>")
        sys.exit(1)

    path = sys.argv[1]
    print(f"Analyzing Qt signals and slots in: {path}")
    
    analyzers = analyze_project(path)
    
    if not analyzers:
        print("No Python files found or analyzed.")
        sys.exit(1)
    
    print(f"Analyzed {len(analyzers)} files")
    
    # Print summary
    total_classes = sum(len(a.classes) for a in analyzers)
    total_signals = sum(len(data['signals']) for a in analyzers for data in a.classes.values())
    total_slots = sum(len(data['slots']) for a in analyzers for data in a.classes.values())
    total_connections = sum(len(a.connections) for a in analyzers)
    
    print(f"Found: {total_classes} classes, {total_signals} signals, {total_slots} slots, {total_connections} connections")
    
    if generate_graph(analyzers, output_path='signal_slot_graph.dot'):
        print("Graph generation completed successfully!")
    else:
        print("Graph generation failed. Check error messages above.")