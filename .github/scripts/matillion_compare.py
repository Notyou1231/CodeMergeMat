import json
import sys

def compare_matillion_json(old_version, new_version):
    changes = []
    
    try:
        # Compare job info
        if old_version.get("info", {}).get("name") != new_version.get("info", {}).get("name"):
            changes.append(f"Job name changed: {old_version.get('info', {}).get('name')} -> {new_version.get('info', {}).get('name')}")
        
        if old_version.get("info", {}).get("description") != new_version.get("info", {}).get("description"):
            changes.append(f"Job description changed: {old_version.get('info', {}).get('description')} -> {new_version.get('info', {}).get('description')}")
        
        # Compare components
        old_components = old_version.get("job", {}).get("components", {})
        new_components = new_version.get("job", {}).get("components", {})
        
        def get_parameter_by_name(component, param_name):
            for param in component.get("parameters", {}).values():
                if param.get("name") == param_name:
                    return param.get("elements", {}).get("1", {}).get("values", {}).get("1", {}).get("value")
            return None

        # Track added/removed/modified components
        for comp_id in set(old_components.keys()) | set(new_components.keys()):
            if comp_id not in old_components:
                comp_name = get_parameter_by_name(new_components[comp_id], "Name")
                changes.append(f"➕ Added component: {comp_name}")
            elif comp_id not in new_components:
                comp_name = get_parameter_by_name(old_components[comp_id], "Name")
                changes.append(f"➖ Removed component: {comp_name}")
            else:
                old_comp = old_components[comp_id]
                new_comp = new_components[comp_id]
                
                # Get component name
                old_name = get_parameter_by_name(old_comp, "Name")
                new_name = get_parameter_by_name(new_comp, "Name")
                
                if old_name != new_name:
                    changes.append(f"📝 Component renamed: {old_name} -> {new_name}")
                
                # Compare Target Table
                old_table = get_parameter_by_name(old_comp, "Target Table")
                new_table = get_parameter_by_name(new_comp, "Target Table")
                if old_table and new_table and old_table != new_table:
                    changes.append(f"🎯 Target table changed in {new_name}: {old_table} -> {new_table}")
                
                # Compare SQL Query
                old_sql = get_parameter_by_name(old_comp, "SQL Query")
                new_sql = get_parameter_by_name(new_comp, "SQL Query")
                if old_sql and new_sql and old_sql != new_sql:
                    changes.append(f"📊 SQL Query modified in {new_name}")
                
                # Compare Schema
                old_schema = get_parameter_by_name(old_comp, "Schema")
                new_schema = get_parameter_by_name(new_comp, "Schema")
                if old_schema and new_schema and old_schema != new_schema:
                    changes.append(f"📊 Schema changed in {new_name}: {old_schema} -> {new_schema}")
                
                # Compare Database
                old_db = get_parameter_by_name(old_comp, "Database")
                new_db = get_parameter_by_name(new_comp, "Database")
                if old_db and new_db and old_db != new_db:
                    changes.append(f"🗄️ Database changed in {new_name}: {old_db} -> {new_db}")
                
                # Compare Column Names if present
                old_columns = {}
                new_columns = {}
                
                for param in old_comp.get("parameters", {}).values():
                    if param.get("name") == "Column Names":
                        for element in param.get("elements", {}).values():
                            col_value = element.get("values", {}).get("1", {}).get("value")
                            if col_value:
                                old_columns[col_value] = True
                
                for param in new_comp.get("parameters", {}).values():
                    if param.get("name") == "Column Names":
                        for element in param.get("elements", {}).values():
                            col_value = element.get("values", {}).get("1", {}).get("value")
                            if col_value:
                                new_columns[col_value] = True
                
                # Compare columns
                added_cols = set(new_columns.keys()) - set(old_columns.keys())
                removed_cols = set(old_columns.keys()) - set(new_columns.keys())
                
                for col in added_cols:
                    changes.append(f"➕ Added column in {new_name}: {col}")
                for col in removed_cols:
                    changes.append(f"➖ Removed column in {new_name}: {col}")
                
                # Compare Column Mapping if present
                old_mappings = {}
                new_mappings = {}
                
                for param in old_comp.get("parameters", {}).values():
                    if param.get("name") == "Column Mapping":
                        for element in param.get("elements", {}).values():
                            source = element.get("values", {}).get("1", {}).get("value")
                            target = element.get("values", {}).get("2", {}).get("value")
                            if source and target:
                                old_mappings[source] = target
                
                for param in new_comp.get("parameters", {}).values():
                    if param.get("name") == "Column Mapping":
                        for element in param.get("elements", {}).values():
                            source = element.get("values", {}).get("1", {}).get("value")
                            target = element.get("values", {}).get("2", {}).get("value")
                            if source and target:
                                new_mappings[source] = target
                
                # Compare mappings
                for source in set(old_mappings.keys()) | set(new_mappings.keys()):
                    if source not in old_mappings:
                        changes.append(f"➕ Added mapping in {new_name}: {source} -> {new_mappings[source]}")
                    elif source not in new_mappings:
                        changes.append(f"➖ Removed mapping in {new_name}: {source} -> {old_mappings[source]}")
                    elif old_mappings[source] != new_mappings[source]:
                        changes.append(f"📝 Modified mapping in {new_name}: {source}: {old_mappings[source]} -> {new_mappings[source]}")

        # Compare variables
        old_vars = old_version.get("job", {}).get("variables", {})
        new_vars = new_version.get("job", {}).get("variables", {})
        
        for var_name in set(old_vars.keys()) | set(new_vars.keys()):
            if var_name not in old_vars:
                changes.append(f"➕ Added variable: {var_name}")
            elif var_name not in new_vars:
                changes.append(f"➖ Removed variable: {var_name}")
            elif old_vars[var_name] != new_vars[var_name]:
                changes.append(f"📝 Modified variable: {var_name}")

    except Exception as e:
        changes.append(f"❌ Error analyzing changes: {str(e)}")
    
    return changes

def main():
    if len(sys.argv) != 3:
        print("Usage: python matillion_compare.py old_version.json new_version.json")
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r') as f:
            old_version = json.load(f)
        with open(sys.argv[2], 'r') as f:
            new_version = json.load(f)

        changes = compare_matillion_json(old_version, new_version)
        
        if not changes:
            print("No significant changes detected")
        else:
            print("Changes detected:")
            for change in changes:
                print(f"- {change}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
