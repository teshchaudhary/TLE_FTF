class Solution:
    def smallestWindow(self, s, p):
        print(s, p)
        n = len(s)
        m = len(p)
        if not s or not p:
            return ""
        from collections import defaultdict    
        count = defaultdict(int)
        for i in range(m):
            count[p[i]]+=1
        window = defaultdict(int)    
        
        total = 0
        i = 0
        ans = ""
        start = None
        end = None
        ans_len = float("inf")
        for j in range(n):
            if s[j] in count:
                window[s[j]]+=1
                if window[s[j]] <= count[s[j]]:
                    total+=1
            print(total)    
            print(window)    
            print("F",s[i:j+1])    
            while total == m and i <= j:
                if total == m and j-i+1 < ans_len:
                    start = i
                    end = j
                    ans_len = j-i+1
                    print("ans:",s[i:j+1], ans_len)

                if s[i] in count:
                    if window[s[i]] == count[s[i]]:
                        total-=1
                    window[s[i]]-=1           
                i+=1    
            print("S",s[i:j+1])
                #shrink
        if ans_len == float("inf"):
            return ""
        print( s[start:end+1]     )        


        # print( s[start:end+1] )      
s = "uvuuuvv"
p = "uuvu"              
Solution().smallestWindow(s, p)                