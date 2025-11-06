# Users Table Clarification

## What is the "Users" Table?

The **`users` table** would be for **platform users** (admins, marketers, analysts) who **use** the CDP platform, NOT customer data.

### Platform Users vs Customers

**Platform Users (`users` table):**
- Platform administrators
- Marketing team members
- Data analysts
- People who log into the CDP platform UI
- Need authentication (email/password)
- Have roles/permissions (admin, marketer, viewer)
- Belong to tenants/organizations

**Customers (`customers` table):**
- Your actual customers (end users)
- People who buy your products/services
- Already exists in `cdp_platform.core.customers`
- This is customer data, not platform users

### Example Users Table Structure

```sql
CREATE TABLE cdp_platform.core.users (
    user_id STRING NOT NULL,
    tenant_id STRING NOT NULL,
    email STRING NOT NULL,
    password_hash STRING NOT NULL,  -- bcrypt hashed
    name STRING,
    role STRING,  -- 'admin', 'marketer', 'viewer'
    is_active BOOLEAN,
    last_login TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### Current Status

**Currently:** Authentication uses JWT tokens but doesn't validate against a database. Login accepts any email/tenant_id combination in development mode.

**What's Needed:** Create `users` table and update login to:
1. Look up user by email
2. Verify password hash
3. Check if user is active
4. Check tenant_id matches
5. Generate JWT token

### Do You Need This?

**If you're using Databricks workspace authentication:**
- You might not need a separate `users` table
- Databricks Apps can use workspace users automatically
- JWT tokens can be issued by Databricks

**If you need custom user management:**
- Create `users` table
- Implement password hashing
- Add user registration/login endpoints

**For now:** The current JWT authentication works for development. The `users` table is optional and only needed if you want custom user management separate from Databricks workspace users.

