 # ! / u s r / b i n / b a s h  # TODO: needs to be adopted to PS1
  
 #   t h i s   f i l e   s h o u l d   b e   s o u r c e d   f o r   s h e l l   t o   e x p o r t   p r o j e c t ' s   e n v i r o n m e n t  
  
 u s a g e ( )   {  
         p r i n t f   " U s a g e :   $ 0   [ p a t h   t o   s a n d b o x ] \ n "  
         p r i n t f   " D e s c r i p t i o n : \ n "  
         p r i n t f   "     S o u r c e   p r o j e c t   e n v i r o n m e n t   f r o m   p a t h   t o   s a n d b o x . \ n "  
         p r i n t f   "     C u r r e n t   w o r k i n g   d i r e c t o r y   i s   u s e d   i f   p a t h   i s   n o t   p r o v i d e d . \ n "  
 }  
  
 m y f a u l t = 0  
  
 i f   [   $ #   - g t   1   ] ;   t h e n  
         m y f a u l t = 1 ;  
         p r i n t f   " E r r o r :   o n l y   a   s i n g l e   s a n d b o x   p a t h   i s   e x p e c t e d . \ n " ;  
         u s a g e ;  
 f i  
  
 i f   [   $ #   - e q   1   ] ;   t h e n  
         s b o x = $ 1  
         i f   [   !   - d   $ s b o x   ] ;   t h e n  
 	 p r i n t f   " E r r o r :   p r o v i d e d   p a t h   i s   n o t   a   s a n d b o x   d i r e c t o r y \ n "  
 	 u s a g e  
 	 m y f a u l t = 1  
         f i  
 e l s e  
         s b o x = ' . '  
 f i  
  
 i f   [   $ m y f a u l t   - e q   0   ] ;   t h e n  
         t e m p f o o = " e x p o r t _ proje n v . s h "  
         T M P F I L E = ` m k t e m p   / t m p / $ { t e m p f o o } . X X X X X X `  
         i f   [   $ ?   - e q   0   ] ;   t h e n  
 	 v a r s = $ ( e x p o r t _ proje n v . p y   - s   $ s b o x   2 > $ T M P F I L E )  
 	 i f   [   $ ?   - e q   0   ] ;   t h e n  
                         e c h o   $ v a r s   >   $ T M P F I L E  
 	         .   $ T M P F I L E  
 	         f o r   d   i n   $ ( f i n d   $ A C _ P R O J _ L O C   - t y p e   d   |   g r e p   - v   ' _ _ $ ' ) ;   d o  
 	               b = $ ( b a s e n a m e   $ d )    
 	               i f   [   $ { b : 0 : 1 }   ! =   ' . '   ] ;   t h e n  
 	                       p y a d d s = $ { d } $ { p y a d d s : + : } $ { p y a d d s }  
 	               f i  
 	         d o n e  
 	         e x p o r t   P Y T H O N P A T H = $ { p y a d d s } $ { P Y T H O N P A T H : + : } $ P Y T H O N P A T H  
 	         r m   $ T M P F I L E  
 	 e l s e  
 	         p r i n t f   " E r r o r :   f a i l e d   t o   c r e a t e   e n v i r o n m e n t   f o r   p r o j e c t \ n "  
 	         p r i n t f   " M e s s a g e : \ n "  
 	         c a t   $ T M P F I L E  
 	         r m   $ T M P F I L E  
 	 f i  
         e l s e  
                 p r i n t f   " E r r o r :   f a i l e d   t o   c r e a t e   t e m p o r a r y   e n v i r o n m e n t   f i l e . \ n "  
 	 p r i n t f   " P o s s i b l e   c o r r e c t i o n : \ n "  
 	 p r i n t f   "     1 .   M a k e   s u r e   $ T M P D I R   i s   d e f i n e d \ n "  
 	 p r i n t f   "     2 .   M a k e   s u r e   w r i t i n g   p e r m i s s i o n s   t o   $ T M P D I R \ n "  
         f i  
 f i  
  
