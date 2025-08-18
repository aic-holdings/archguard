"""
Test fixtures for large function detection

This file contains functions of various sizes for testing size detection.
"""

def small_function():
    """A properly sized function"""
    return "Hello, World!"

def medium_function():
    """A medium-sized function"""
    data = []
    for i in range(10):
        if i % 2 == 0:
            data.append(i * 2)
        else:
            data.append(i * 3)
    
    return sum(data)

def large_function_example():
    """
    This function is intentionally large to test detection.
    It violates the single responsibility principle and should be refactored.
    """
    # Data validation section
    results = []
    errors = []
    
    # Input processing
    for i in range(100):
        if i < 0:
            errors.append(f"Negative value: {i}")
            continue
            
        if i % 10 == 0:
            print(f"Processing batch starting at {i}")
        
        # Complex calculation logic
        if i % 2 == 0:
            value = i * 2
            
            # Nested validation
            if value > 100:
                value = value / 2
                
                # More nested logic
                if value > 50:
                    value = value - 10
                    
                    # Even deeper nesting
                    if value > 40:
                        value = 40
        else:
            value = i * 3
            
            # Different validation path
            if value > 150:
                value = 150
                
                # Parallel nested logic
                if value > 100:
                    value = value - 20
        
        # Data transformation
        transformed_value = {
            'original': i,
            'calculated': value,
            'timestamp': time.time(),
            'batch': i // 10,
            'is_even': i % 2 == 0,
            'category': 'high' if value > 50 else 'low'
        }
        
        # Additional processing
        if transformed_value['category'] == 'high':
            transformed_value['priority'] = 1
            transformed_value['requires_review'] = True
            
            # Special handling for high values
            if transformed_value['calculated'] > 80:
                transformed_value['alert'] = True
                transformed_value['escalation_needed'] = True
        else:
            transformed_value['priority'] = 2
            transformed_value['requires_review'] = False
        
        # Quality checks
        if transformed_value['calculated'] < 0:
            errors.append(f"Negative calculation result for input {i}")
            continue
        
        # Data enrichment
        transformed_value['metadata'] = {
            'processed_by': 'large_function_example',
            'version': '1.0',
            'algorithm': 'complex_calculation'
        }
        
        # Final validation
        if all(key in transformed_value for key in ['original', 'calculated', 'timestamp']):
            results.append(transformed_value)
        else:
            errors.append(f"Missing required fields for input {i}")
    
    # Post-processing aggregation
    summary = {
        'total_processed': len(results),
        'total_errors': len(errors),
        'high_priority_count': len([r for r in results if r['priority'] == 1]),
        'average_value': sum(r['calculated'] for r in results) / len(results) if results else 0,
        'max_value': max(r['calculated'] for r in results) if results else 0,
        'min_value': min(r['calculated'] for r in results) if results else 0
    }
    
    # Error reporting
    if errors:
        print(f"Processing completed with {len(errors)} errors:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    
    # Success reporting
    if results:
        print(f"Successfully processed {len(results)} items")
        print(f"Average value: {summary['average_value']:.2f}")
        print(f"Value range: {summary['min_value']} - {summary['max_value']}")
    
    return {
        'results': results,
        'summary': summary,
        'errors': errors,
        'success': len(errors) == 0
    }

def appropriately_sized_function():
    """A function that's at the boundary but still appropriate"""
    config = load_configuration()
    
    # Validate configuration
    if not validate_config(config):
        raise ValueError("Invalid configuration")
    
    # Process data
    data = fetch_data(config)
    processed = transform_data(data)
    
    # Save results
    save_results(processed)
    
    return {
        'status': 'success',
        'items_processed': len(processed),
        'config_version': config.get('version', 'unknown')
    }

def very_large_function_with_multiple_responsibilities():
    """
    This function is extremely large and violates multiple principles.
    It should definitely be detected and refactored.
    """
    # Database connection setup
    connection_string = "postgresql://user:pass@localhost/db"
    connection = create_connection(connection_string)
    cursor = connection.cursor()
    
    # User management logic
    users = []
    user_query = "SELECT * FROM users WHERE active = true"
    cursor.execute(user_query)
    raw_users = cursor.fetchall()
    
    for raw_user in raw_users:
        user = {
            'id': raw_user[0],
            'username': raw_user[1],
            'email': raw_user[2],
            'created_at': raw_user[3],
            'last_login': raw_user[4],
            'profile_complete': raw_user[5]
        }
        
        # User validation
        if not user['email'] or '@' not in user['email']:
            print(f"Invalid email for user {user['id']}")
            continue
        
        # Profile completion check
        if not user['profile_complete']:
            # Send reminder email
            email_body = f"""
            Dear {user['username']},
            
            Please complete your profile to access all features.
            
            Best regards,
            The Team
            """
            send_email(user['email'], "Complete Your Profile", email_body)
        
        # Activity analysis
        if user['last_login']:
            days_since_login = (datetime.now() - user['last_login']).days
            
            if days_since_login > 30:
                user['status'] = 'inactive'
                
                # Inactive user handling
                inactive_email = f"""
                Dear {user['username']},
                
                We notice you haven't logged in for {days_since_login} days.
                
                Best regards,
                The Team
                """
                send_email(user['email'], "We Miss You", inactive_email)
            elif days_since_login > 7:
                user['status'] = 'low_activity'
            else:
                user['status'] = 'active'
        else:
            user['status'] = 'never_logged_in'
        
        users.append(user)
    
    # Order processing logic (should be separate function)
    orders = []
    order_query = "SELECT * FROM orders WHERE status = 'pending'"
    cursor.execute(order_query)
    raw_orders = cursor.fetchall()
    
    for raw_order in raw_orders:
        order = {
            'id': raw_order[0],
            'user_id': raw_order[1],
            'total': raw_order[2],
            'items': json.loads(raw_order[3]),
            'created_at': raw_order[4],
            'shipping_address': raw_order[5]
        }
        
        # Order validation
        if order['total'] <= 0:
            print(f"Invalid order total for order {order['id']}")
            continue
        
        # Inventory check
        for item in order['items']:
            inventory_query = f"SELECT stock FROM inventory WHERE product_id = {item['product_id']}"
            cursor.execute(inventory_query)
            stock_result = cursor.fetchone()
            
            if not stock_result or stock_result[0] < item['quantity']:
                print(f"Insufficient stock for product {item['product_id']}")
                # Cancel order logic
                cancel_query = f"UPDATE orders SET status = 'cancelled' WHERE id = {order['id']}"
                cursor.execute(cancel_query)
                break
        else:
            # Process order if all items available
            for item in order['items']:
                # Update inventory
                update_query = f"""
                UPDATE inventory 
                SET stock = stock - {item['quantity']} 
                WHERE product_id = {item['product_id']}
                """
                cursor.execute(update_query)
            
            # Update order status
            status_query = f"UPDATE orders SET status = 'processing' WHERE id = {order['id']}"
            cursor.execute(status_query)
            
            orders.append(order)
    
    # Reporting logic (should be separate function)
    report = {
        'users': {
            'total': len(users),
            'active': len([u for u in users if u['status'] == 'active']),
            'inactive': len([u for u in users if u['status'] == 'inactive']),
            'never_logged_in': len([u for u in users if u['status'] == 'never_logged_in'])
        },
        'orders': {
            'total_processed': len(orders),
            'total_value': sum(o['total'] for o in orders),
            'average_order_value': sum(o['total'] for o in orders) / len(orders) if orders else 0
        }
    }
    
    # Generate and save report
    report_text = f"""
    Daily Report - {datetime.now().strftime('%Y-%m-%d')}
    
    Users:
    - Total Active Users: {report['users']['total']}
    - Active: {report['users']['active']}
    - Inactive: {report['users']['inactive']}
    - Never Logged In: {report['users']['never_logged_in']}
    
    Orders:
    - Orders Processed: {report['orders']['total_processed']}
    - Total Value: ${report['orders']['total_value']:.2f}
    - Average Order Value: ${report['orders']['average_order_value']:.2f}
    """
    
    with open(f"daily_report_{datetime.now().strftime('%Y%m%d')}.txt", 'w') as f:
        f.write(report_text)
    
    # Clean up
    cursor.close()
    connection.close()
    
    return report