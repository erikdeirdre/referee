""" Includes Row Count in Graphql Queries """
from graphene import (Interface, Int, Boolean, String, ID, ObjectType, Date,
                      InputObjectType)


class TotalCount(Interface):
    """ Return Row Count """
    total_count = Int()

    def resolve_total_count(self, info):
        """  Return Row Count """
        return self.length
