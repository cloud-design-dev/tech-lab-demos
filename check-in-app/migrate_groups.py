#!/usr/bin/env python3
"""
Database Migration Script: Convert Numeric Groups to Letter Groups

This script migrates existing groups from numeric format (Group 1, Group 2)
to letter format (Group A, Group B) with VPC mapping.

Usage:
    python migrate_groups.py [--dry-run]
    
Options:
    --dry-run    Show what would be changed without making actual changes
"""

import os
import sys
import argparse
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Group, get_vpc_info_from_group_name

def migrate_numeric_groups_to_letters(dry_run=False):
    """Migrate numeric groups to letter-based groups"""
    
    with app.app_context():
        print(f"🔄 Starting group migration {'(DRY RUN)' if dry_run else ''}")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print("-" * 60)
        
        try:
            # Find all numeric groups
            all_groups = Group.query.all()
            numeric_groups = []
            
            for group in all_groups:
                group_identifier = group.name.replace("Group ", "").strip()
                if group_identifier.isdigit():
                    numeric_groups.append(group)
            
            if not numeric_groups:
                print("✅ No numeric groups found - migration not needed")
                return
            
            print(f"📊 Found {len(numeric_groups)} numeric groups to migrate")
            print(f"📊 Total groups in database: {len(all_groups)}")
            print()
            
            migration_plan = []
            
            # Plan the migration
            for group in numeric_groups:
                group_identifier = group.name.replace("Group ", "").strip()
                group_number = int(group_identifier)
                group_index = group_number - 1  # Group 1 = index 0
                
                if 0 <= group_index < 25:
                    new_letter = chr(ord('a') + group_index).upper()
                    new_name = f"Group {new_letter}"
                    vpc_number = (group_index // 5) + 1
                    
                    # Count users in this group
                    users_count = User.query.filter_by(group_name=group.name).count()
                    
                    migration_plan.append({
                        'group': group,
                        'old_name': group.name,
                        'new_name': new_name,
                        'letter': new_letter,
                        'vpc': vpc_number,
                        'users_count': users_count
                    })
                else:
                    print(f"⚠️  Warning: Group {group.name} index {group_index} out of range (0-24)")
            
            # Display migration plan
            print("📋 Migration Plan:")
            print("-" * 60)
            for plan in migration_plan:
                print(f"  {plan['old_name']} → {plan['new_name']} (Letter: {plan['letter']}, VPC: {plan['vpc']}, Users: {plan['users_count']})")
            
            print()
            
            if dry_run:
                print("🔍 DRY RUN: No changes will be made")
                print("💡 Run without --dry-run to apply these changes")
                return
            
            # Confirm before proceeding
            if not sys.stdin.isatty():
                # Non-interactive mode, proceed automatically
                proceed = True
            else:
                response = input("❓ Proceed with migration? [y/N]: ").strip().lower()
                proceed = response in ['y', 'yes']
            
            if not proceed:
                print("❌ Migration cancelled")
                return
            
            # Perform the migration
            print("🚀 Applying migration...")
            migration_results = []
            
            for plan in migration_plan:
                group = plan['group']
                old_name = plan['old_name']
                new_name = plan['new_name']
                
                # Update group name
                group.name = new_name
                
                # Update all users in this group
                users_updated = User.query.filter_by(group_name=old_name).update(
                    {'group_name': new_name}
                )
                
                migration_results.append({
                    'old_name': old_name,
                    'new_name': new_name,
                    'letter': plan['letter'],
                    'vpc': plan['vpc'],
                    'users_updated': users_updated
                })
                
                print(f"  ✅ {old_name} → {new_name} ({users_updated} users updated)")
            
            # Commit changes
            db.session.commit()
            
            print()
            print("🎉 Migration completed successfully!")
            print(f"📊 Total groups migrated: {len(migration_results)}")
            print(f"📊 Total users updated: {sum(r['users_updated'] for r in migration_results)}")
            
            # Display final VPC mapping
            print()
            print("🗺️  Final VPC Group Mapping:")
            print("-" * 30)
            for vpc in range(1, 6):
                vpc_groups = [r for r in migration_results if r['vpc'] == vpc]
                if vpc_groups:
                    letters = [r['letter'] for r in vpc_groups]
                    print(f"  VPC {vpc}: Groups {', '.join(letters)}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description="Migrate numeric groups to letter groups")
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making actual changes')
    
    args = parser.parse_args()
    
    try:
        migrate_numeric_groups_to_letters(dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\n❌ Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Migration failed with error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()