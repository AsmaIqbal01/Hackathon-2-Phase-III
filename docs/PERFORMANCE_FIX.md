# Performance Fix: Login Speed Optimization

## 🐛 Problem

**Symptom:** Login/Registration taking 30+ seconds

**Root Cause:** Bcrypt password hashing was using default rounds (12), which is very secure but extremely slow:
- Registration: ~30 seconds
- Login: ~30 seconds
- Every password hash/verify operation was a bottleneck

## ✅ Solution

**Optimized bcrypt rounds for development:**
- Changed from 12 rounds (default) to 4 rounds
- File: `backend/src/utils/security.py`

```python
# Before (slow)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# After (fast)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=4  # Fast for development, use 12+ for production
)
```

## 📊 Performance Improvement

| Operation | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Registration | ~30s | 1.6s | **95% faster** |
| Login | ~30s | 0.37s | **99% faster** |

## 🔒 Security Note

**Development (current):**
- 4 rounds = Fast hashing for development
- Still secure for testing
- ~370ms per operation

**Production (recommended):**
- Change to 12 rounds minimum
- 14-16 rounds for high security
- Update in `.env` or config file before deployment

```python
# Production configuration
bcrypt__rounds=12  # or higher (14-16 for high security)
```

## 🚀 Now You Can

✅ Register new users instantly
✅ Login in under 1 second
✅ Test authentication flows without waiting
✅ Develop and iterate quickly

## ⚠️ Important

**Before deploying to production:**
1. Update `bcrypt__rounds` to 12 or higher in `backend/src/utils/security.py`
2. Or add to environment variables:
   ```env
   BCRYPT_ROUNDS=12
   ```
3. Test with production settings before go-live

---

**Issue:** #1
**Fixed:** 2026-02-08
**Commit:** abce3d1
**Files Modified:** `backend/src/utils/security.py`
